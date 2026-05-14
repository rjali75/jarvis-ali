"""Outils visuels : cartes et globe 3D style Jarvis."""
import os
import tempfile
import time
import webbrowser

import folium
import plotly.graph_objects as go
from geopy.geocoders import Nominatim

from jarvis.tools.registry import tool


# Geocoder partage (Nominatim = OpenStreetMap, gratuit, sans cle)
_GEOCODER = Nominatim(user_agent="jarvis-ali")
_GEOCODE_CACHE: dict[str, tuple[float, float]] = {}


def _geocode(place: str) -> tuple[float, float] | None:
    """Trouve les coordonnees (lat, lon) d'un lieu. Cache pour eviter le rate limit."""
    if place in _GEOCODE_CACHE:
        return _GEOCODE_CACHE[place]

    try:
        time.sleep(1)  # politesse envers Nominatim (1 req/sec max)
        location = _GEOCODER.geocode(place, timeout=10)
        if location:
            coords = (location.latitude, location.longitude)
            _GEOCODE_CACHE[place] = coords
            return coords
    except Exception:
        pass
    return None


@tool
def show_globe(places: str) -> str:
    """Affiche un globe 3D interactif (style Iron Man) avec des markers sur les lieux.

    Le globe s'oriente automatiquement vers les lieux demandes.
    Tu peux faire tourner a la souris, zoomer, et survoler les markers.

    Args:
        places: Liste de lieux separes par des virgules.
                Ex: "Tokyo, Paris, New York" affichera 3 markers sur le globe.
                Pour un globe vide sans markers, passe "monde" ou "world".

    A utiliser quand l'utilisateur veut une vue globale, plusieurs lieux,
    ou demande explicitement un globe / une vue de la Terre.
    """
    place_list = [p.strip() for p in places.split(",") if p.strip()]
    is_world_view = len(place_list) == 1 and place_list[0].lower() in ("monde", "world", "terre", "earth")

    fig = go.Figure()

    # Geocode tous les lieux (sauf vue globale)
    lats, lons, names = [], [], []
    not_found = []

    if not is_world_view and place_list:
        for place in place_list:
            coords = _geocode(place)
            if coords:
                lats.append(coords[0])
                lons.append(coords[1])
                names.append(place)
            else:
                not_found.append(place)

    # Centrage automatique sur la moyenne des markers
    if lats:
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)
    else:
        center_lat, center_lon = 20, 10  # vue par defaut Europe/Afrique

    # Ajouter les markers (gros et visibles)
    if lats:
        # Halo de fond (cercle plus grand, semi-transparent)
        fig.add_trace(go.Scattergeo(
            lat=lats,
            lon=lons,
            mode="markers",
            marker=dict(
                size=35,
                color="#00FFFF",
                opacity=0.25,
                line=dict(width=0),
            ),
            hoverinfo="skip",
            showlegend=False,
        ))
        # Marker principal au-dessus
        fig.add_trace(go.Scattergeo(
            lat=lats,
            lon=lons,
            text=names,
            mode="markers+text",
            marker=dict(
                size=14,
                color="#00FFFF",
                line=dict(width=2, color="#FFFFFF"),
                symbol="circle",
                opacity=1.0,
            ),
            textposition="top center",
            textfont=dict(color="#00FFFF", size=15, family="Courier New, monospace"),
            hoverinfo="text",
            showlegend=False,
        ))

    # Configuration du globe (theme dark Jarvis-style)
    fig.update_geos(
        projection_type="orthographic",
        projection=dict(rotation=dict(lon=center_lon, lat=center_lat, roll=0)),
        showland=True,
        landcolor="rgb(40, 45, 60)",
        showocean=True,
        oceancolor="rgb(5, 10, 25)",
        showcoastlines=True,
        coastlinecolor="rgb(100, 180, 255)",
        coastlinewidth=0.5,
        showcountries=True,
        countrycolor="rgba(80, 120, 160, 0.5)",
        countrywidth=0.3,
        showlakes=True,
        lakecolor="rgb(5, 10, 25)",
        bgcolor="rgb(0, 5, 15)",
        lonaxis=dict(showgrid=True, gridcolor="rgba(50, 100, 180, 0.12)", gridwidth=0.5),
        lataxis=dict(showgrid=True, gridcolor="rgba(50, 100, 180, 0.12)", gridwidth=0.5),
    )

    fig.update_layout(
        title=dict(
            text="JARVIS · Global View",
            font=dict(color="#00FFFF", size=20, family="Courier New, monospace"),
            x=0.5,
        ),
        paper_bgcolor="rgb(0, 5, 15)",
        height=800,
        margin=dict(l=0, r=0, t=60, b=0),
    )

    # Sauvegarder et ouvrir
    html_path = os.path.join(tempfile.gettempdir(), "jarvis_globe.html")
    fig.write_html(html_path)
    webbrowser.open(f"file://{html_path}")

    if is_world_view:
        return "Globe ouvert dans le navigateur. Vue de la Terre, prete a explorer."

    found_msg = f"Globe ouvert avec markers sur : {', '.join(names)}." if lats else "Globe ouvert (aucun lieu localise)."
    if not_found:
        found_msg += f" (Pas trouve : {', '.join(not_found)})"
    return found_msg


@tool
def show_map(location: str, zoom: int = 12) -> str:
    """Affiche une carte 2D interactive zoomee sur un lieu precis (theme dark Jarvis).

    Args:
        location: Nom du lieu (ville, monument, adresse, pays).
                  Ex: "Tour Eiffel Paris", "Tokyo", "Times Square New York"
        zoom: Niveau de zoom (1=monde, 10=ville, 15=quartier, 18=rue). Defaut 12.

    A utiliser quand l'utilisateur veut voir UN lieu precis sur une carte.
    Pour plusieurs lieux ou une vue globale, utilise show_globe() a la place.
    """
    coords = _geocode(location)
    if not coords:
        return f"Impossible de localiser '{location}'. Verifie l'orthographe."

    m = folium.Map(
        location=coords,
        zoom_start=zoom,
        tiles="CartoDB dark_matter",  # theme dark Jarvis
        control_scale=True,
    )

    folium.Marker(
        coords,
        popup=folium.Popup(location, max_width=300),
        tooltip=location,
        icon=folium.Icon(color="lightblue", icon="info-sign"),
    ).add_to(m)

    # Cercle d'emphase autour du marker
    folium.Circle(
        coords,
        radius=500,
        color="#00FFFF",
        fill=True,
        fillColor="#00FFFF",
        fillOpacity=0.1,
        weight=2,
    ).add_to(m)

    html_path = os.path.join(tempfile.gettempdir(), "jarvis_map.html")
    m.save(html_path)
    webbrowser.open(f"file://{html_path}")

    return f"Carte ouverte sur {location} (zoom {zoom})."