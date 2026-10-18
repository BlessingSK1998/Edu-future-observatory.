"""Run the existing interactive dashboard on Streamlit."""
from pathlib import Path
import base64
import mimetypes
import re
import streamlit as st
import streamlit.components.v1 as components

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "docs"
st.set_page_config(page_title="EDU / FUTURE", layout="wide")
st.caption("EDU / FUTURE · Created by Blessing Sekeramavi")

def asset_url(name):
    path = (WEB / name).resolve()
    if not path.is_relative_to(WEB.resolve()) or not path.is_file():
        raise ValueError(f"Missing dashboard asset: {name}")
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return "data:" + mime + ";base64," + base64.b64encode(path.read_bytes()).decode()

def script(name):
    source = (WEB / name).read_text(encoding="utf-8")
    source = re.sub(r"fetch\((['\"])([^'\"]+)\1\)", lambda m: "fetch(" + repr(asset_url(m[2])) + ")" if not m[2].startswith(("http:", "https:", "data:")) else m[0], source)
    return "<script>" + source.replace("</script", "<\\/script") + "</script>"

@st.cache_data
def dashboard():
    page = (WEB / "index.html").read_text(encoding="utf-8")
    scripts = []
    geo = WEB / "geo/world_110m.json"
    if geo.exists():
        scripts.append("<script>window.PlotlyGeoAssets={topojson:{world_110m:" + geo.read_text(encoding="utf-8").replace("</script", "<\\/script") + "}};</script>")
    def add_script(match):
        name = match[1]
        if name.startswith(("http:", "https:")):
            scripts.append(match[0])
        else:
            scripts.append(script(name))
        return ""
    page = re.sub(r'<script[^>]*src="([^"]+)"[^>]*>\s*</script>', add_script, page)
    page = re.sub(r'<link[^>]*href="([^"]+\.css)"[^>]*>', lambda m: "<style>" + (WEB / m[1]).read_text(encoding="utf-8") + "</style>", page)
    page = re.sub(r'href="([^"]+)"', lambda m: 'href="' + asset_url(m[1]) + '"' if not m[1].startswith(("#", "http:", "https:", "mailto:", "data:")) and (WEB / m[1]).is_file() else m[0], page)
    return page.replace("</body>", "".join(scripts) + "</body>") if "</body>" in page else page + "".join(scripts)

components.html(dashboard(), height=1600, scrolling=True)
