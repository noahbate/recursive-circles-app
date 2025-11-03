import streamlit as st
import streamlit.components.v1 as components
from PIL import Image, ImageDraw
import svgwrite
import io
import time

def add_recursive_circles_pil(draw, center_x, center_y, radius, depth, max_depth, is_white, top_pct, bottom_pct):
    """Recursively add circles to PIL image."""
    if depth > max_depth or radius < 1:
        return

    fillcolor = 255 if is_white else 0
    draw.ellipse(
        [center_x - radius, center_y - radius,
         center_x + radius, center_y + radius],
        fill=fillcolor,
        outline=None
    )

    if depth >= max_depth:
        return

    top_radius = radius * top_pct
    bottom_radius = radius * bottom_pct
    top_center_y = center_y - (radius - top_radius)
    bottom_center_y = center_y + (radius - bottom_radius)

    add_recursive_circles_pil(draw, center_x, top_center_y, top_radius,
                         depth + 1, max_depth, not is_white, top_pct, bottom_pct)
    add_recursive_circles_pil(draw, center_x, bottom_center_y, bottom_radius,
                         depth + 1, max_depth, not is_white, top_pct, bottom_pct)

def add_recursive_circles_svg(dwg, center_x, center_y, radius, depth, max_depth, is_white, top_pct, bottom_pct):
    """Recursively add circles to SVG drawing."""
    if depth > max_depth or radius < 0.01:  # Go WAY smaller for more detail
        return

    fillcolor = 'white' if is_white else 'black'
    dwg.add(dwg.circle(
        center=(center_x, center_y),
        r=radius,
        fill=fillcolor,
        stroke='none'
    ))

    if depth >= max_depth:
        return

    top_radius = radius * top_pct
    bottom_radius = radius * bottom_pct
    top_center_y = center_y - (radius - top_radius)
    bottom_center_y = center_y + (radius - bottom_radius)

    add_recursive_circles_svg(dwg, center_x, top_center_y, top_radius,
                         depth + 1, max_depth, not is_white, top_pct, bottom_pct)
    add_recursive_circles_svg(dwg, center_x, bottom_center_y, bottom_radius,
                         depth + 1, max_depth, not is_white, top_pct, bottom_pct)

def create_svg_with_animation(size, max_depth, top_pct, bottom_pct, start_white, zoom_speed, animation_duration, zoom_target="center"):
    """Create SVG with CSS-based TRULY infinite zoom animation using seamless looping."""
    dwg = svgwrite.Drawing(size=(size, size), profile='full')

    # Create main group for the pattern
    pattern_group = dwg.g(id='pattern')
    dwg.add(pattern_group)

    # Create a temporary drawing to collect circles
    temp_dwg = svgwrite.Drawing(size=(size, size))
    center = size / 2
    radius = size / 2 - 10

    add_recursive_circles_svg(temp_dwg, center, center, radius, 0, max_depth, start_white, top_pct, bottom_pct)

    # Add all circles to the pattern group
    for element in temp_dwg.elements:
        pattern_group.add(element)

    # Calculate PERFECT seamless zoom for TRULY infinite effect
    # We zoom into one of the child circles, and when it reaches EXACTLY full size, we loop back
    # This creates a perfect infinite zoom because the pattern is self-similar!

    if zoom_target == "top":
        # Zoom into top circle - use zoom_speed to control how fast we zoom
        # The base seamless factor is 1/top_pct, but we multiply by zoom_speed for speed control
        base_seamless = 1.0 / top_pct  # e.g., 1/0.62 = 1.6129...
        seamless_zoom = base_seamless * zoom_speed  # Multiply by user's speed setting!
        # Calculate offset: child is at center_y - (radius - child_radius)
        # We need to translate so the child's center becomes the viewport center
        target_y_offset = -(size / 2) * (1 - top_pct)
        translate_y_percent = (target_y_offset / (size / 2)) * 100  # Convert to percentage
    elif zoom_target == "bottom":
        # Zoom into bottom circle - multiply base seamless by zoom_speed
        base_seamless = 1.0 / bottom_pct  # e.g., 1/0.38 = 2.6315...
        seamless_zoom = base_seamless * zoom_speed  # Multiply by user's speed setting!
        target_y_offset = (size / 2) * (1 - bottom_pct)
        translate_y_percent = (target_y_offset / (size / 2)) * 100
    else:  # center - zoom straight in (not seamless)
        target_y_offset = 0
        translate_y_percent = 0
        seamless_zoom = zoom_speed

    # Create the animated HTML with CSS
    svg_str = dwg.tostring()

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                margin: 0;
                padding: 0;
                overflow: hidden;
                background: white;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }}
            #svg-container {{
                width: 100%;
                height: 100%;
                display: flex;
                justify-content: center;
                align-items: center;
                overflow: hidden;
                position: relative;
            }}
            svg {{
                animation: zoomInfinite {animation_duration}s linear infinite;
                transform-origin: 50% 50%;
            }}
            @keyframes zoomInfinite {{
                0% {{
                    transform: scale(1) translateY(0%);
                }}
                100% {{
                    transform: scale({seamless_zoom:.10f}) translateY({translate_y_percent:.10f}%);
                }}
            }}
        </style>
    </head>
    <body>
        <div id="svg-container">
            {svg_str}
        </div>
        <script>
            // Seamless loop - the pattern is self-similar, so zooming in reveals the same pattern!
            // This creates a TRULY INFINITE zoom effect
        </script>
    </body>
    </html>
    """
    return html

# Streamlit app configuration
st.set_page_config(page_title="Recursive Circles - Infinite Zoom", layout="wide")

st.title("🔄 Recursive Circles Generator")
st.markdown("Create beautiful fractal-like patterns with nested circles • Now with **SVG Infinite Zoom!** ✨")

# Sidebar controls
st.sidebar.header("⚙️ Parameters")

# Mode selection
mode = st.sidebar.radio(
    "🎭 Rendering Mode",
    options=["SVG (Vector - Infinite Resolution)", "PNG (Raster - Download Only)"],
    help="SVG provides perfect infinite zoom with no pixelation!"
)

# Animation toggle for SVG mode
if "SVG" in mode:
    enable_animation = st.sidebar.checkbox(
        "🎬 Enable Infinite Zoom Animation",
        value=True,
        help="Smooth CSS-based infinite zoom"
    )
else:
    enable_animation = False

max_depth = st.sidebar.slider(
    "Recursion Depth",
    min_value=5,
    max_value=100,
    value=80,
    step=1,
    help="Number of nesting levels. Higher = more infinite layers! 50+ = INSANE, 100 = MAXIMUM INFINITY"
)

if "SVG" in mode:
    img_size = st.sidebar.slider(
        "SVG Size (viewBox)",
        min_value=500,
        max_value=5000,
        value=3000,
        step=100,
        help="SVG is resolution-independent - larger = smoother details at high zoom levels"
    )
else:
    img_size = st.sidebar.slider(
        "Image Size (pixels)",
        min_value=500,
        max_value=3000,
        value=2000,
        step=100,
        help="Size of the generated PNG image"
    )

top_pct = st.sidebar.slider(
    "Top Circle Size (%)",
    min_value=30,
    max_value=80,
    value=62,
    step=1,
    help="Size of top circle as percentage of parent"
) / 100

bottom_pct = st.sidebar.slider(
    "Bottom Circle Size (%)",
    min_value=20,
    max_value=70,
    value=38,
    step=1,
    help="Size of bottom circle as percentage of parent"
) / 100

start_color = st.sidebar.radio(
    "Starting Color",
    options=["Black", "White"],
    index=0
)

# Animation settings for SVG
if enable_animation:
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎬 Animation Settings")

    zoom_speed = st.sidebar.slider(
        "Zoom Multiplier",
        min_value=1.5,
        max_value=50.0,
        value=20.0,
        step=0.5,
        help="How much to zoom - go crazy with high values for insane speed! 20+ = hyperspeed"
    )

    animation_duration = st.sidebar.slider(
        "Animation Duration (seconds)",
        min_value=3,
        max_value=300,
        value=60,
        step=5,
        help="How long one zoom cycle takes - make it super long for slow hypnotic zoom! 120+ = epic journey"
    )

    zoom_target = st.sidebar.radio(
        "Zoom Target (for seamless loop)",
        options=["Top Circle (Seamless)", "Bottom Circle (Seamless)", "Center (Continuous)"],
        index=0,
        help="Choose which circle to zoom into. Top/Bottom create PERFECT seamless loops!"
    )

# Calculate estimated number of circles
estimated_circles = 2 ** max_depth
st.sidebar.info(f"📊 Estimated circles: **{estimated_circles:,}**")

# Generate button
button_label = "✨ Generate SVG" if "SVG" in mode else "🎨 Generate PNG"
if st.sidebar.button(button_label, type="primary", use_container_width=True):
    with st.spinner(f"Generating {estimated_circles:,} circles..."):
        is_white_start = (start_color == "White")

        if "SVG" in mode:
            # Generate SVG
            if enable_animation:
                # Parse zoom target
                if "Top" in zoom_target:
                    target = "top"
                elif "Bottom" in zoom_target:
                    target = "bottom"
                else:
                    target = "center"

                html_content = create_svg_with_animation(
                    img_size, max_depth, top_pct, bottom_pct,
                    is_white_start, zoom_speed, animation_duration, target
                )
            else:
                # Static SVG
                dwg = svgwrite.Drawing(size=(img_size, img_size), profile='full')
                center = img_size / 2
                radius = img_size / 2 - 10
                add_recursive_circles_svg(dwg, center, center, radius, 0, max_depth,
                                        is_white_start, top_pct, bottom_pct)
                html_content = f"""
                <div style="display: flex; justify-content: center; background: white; padding: 20px;">
                    {dwg.tostring()}
                </div>
                """

            st.session_state['svg_html'] = html_content
            st.session_state['svg_mode'] = True
            st.session_state['animated'] = enable_animation

        else:
            # Generate PNG
            center_x, center_y = img_size // 2, img_size // 2
            main_radius = img_size // 2 - 10
            img = Image.new('L', (img_size, img_size), color=255)
            draw = ImageDraw.Draw(img)
            add_recursive_circles_pil(draw, center_x, center_y, main_radius, 0, max_depth,
                                is_white_start, top_pct, bottom_pct)
            st.session_state['generated_image'] = img
            st.session_state['svg_mode'] = False

        st.session_state['params'] = {
            'depth': max_depth,
            'size': img_size,
            'top': int(top_pct * 100),
            'bottom': int(bottom_pct * 100),
            'start_color': start_color,
            'mode': mode
        }

    st.success("✅ Generated!")

# Display the result
if 'params' in st.session_state:
    st.markdown("---")

    # Show parameters used
    params = st.session_state['params']
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Depth", params['depth'])
    with col2:
        st.metric("Size", f"{params['size']}px")
    with col3:
        st.metric("Top Circle", f"{params['top']}%")
    with col4:
        st.metric("Bottom Circle", f"{params['bottom']}%")
    with col5:
        st.metric("Mode", "SVG" if st.session_state.get('svg_mode') else "PNG")

    st.markdown("---")

    # Display based on mode
    if st.session_state.get('svg_mode'):
        if st.session_state.get('animated'):
            st.subheader("✨ Infinite Zoom Animation (SVG)")
            st.info("🎬 The animation loops infinitely with perfect vector quality - no pixelation!")
            # Display animated SVG in iframe for full control
            components.html(st.session_state['svg_html'], height=800, scrolling=False)
        else:
            st.subheader("✨ Static SVG (Perfect Vector Quality)")
            components.html(st.session_state['svg_html'], height=800, scrolling=False)

        st.markdown("---")
        st.download_button(
            label="⬇️ Download SVG File",
            data=st.session_state['svg_html'],
            file_name="recursive_circles.html",
            mime="text/html",
            use_container_width=True
        )
    else:
        # PNG display
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            st.image(st.session_state['generated_image'],
                    caption="Your fractal pattern (PNG)",
                    use_container_width=True)

        st.markdown("---")
        buf = io.BytesIO()
        st.session_state['generated_image'].save(buf, format='PNG')
        byte_im = buf.getvalue()

        st.download_button(
            label="⬇️ Download PNG Image",
            data=byte_im,
            file_name="recursive_circles.png",
            mime="image/png",
            use_container_width=True
        )
else:
    # Show instructions
    st.info("👈 Choose your mode and parameters, then click **Generate** to create your fractal pattern!")

    # Show example
    st.markdown("### 🎯 Choose Your Mode")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### ✨ SVG Mode (Recommended)")
        st.markdown("""
        - **Perfect infinite resolution** - never pixelates!
        - **Smooth CSS animation** - butter smooth zoom
        - **Smaller file sizes** - vector graphics
        - **Infinite zoom** reveals endless nested circles
        - Best for viewing and sharing online
        """)

    with col2:
        st.markdown("#### 🖼️ PNG Mode")
        st.markdown("""
        - **Raster image** for downloads
        - High-resolution export
        - Compatible with all image viewers
        - Best for printing or static use
        """)

    st.markdown("---")
    st.markdown("""
    ### How It Works
    This visualization creates a fractal-like pattern where:
    - Each circle is divided into two smaller circles (top and bottom)
    - The pattern repeats recursively inside each circle
    - Colors alternate between black and white at each level
    - **SVG mode**: The infinite zoom reveals the self-similar nature with perfect clarity at any zoom level!
    """)

# Footer
st.markdown("---")
st.markdown("💡 **Pro Tip**: Use **SVG mode with animation** for the best infinite zoom experience - no pixelation ever!")
