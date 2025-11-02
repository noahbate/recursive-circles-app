import streamlit as st
from PIL import Image, ImageDraw
import io

def add_recursive_circles(draw, center_x, center_y, radius, depth, max_depth, is_white, top_pct, bottom_pct):
    """
    Recursively add circles to the image.

    Parameters:
    - draw: PIL ImageDraw object
    - center_x, center_y: Center of the current circle
    - radius: Radius of the current circle
    - depth: Current recursion depth
    - max_depth: Maximum recursion depth
    - is_white: Boolean indicating if current circle should be white
    - top_pct: Percentage of radius for top circle (0-1)
    - bottom_pct: Percentage of radius for bottom circle (0-1)
    """
    if depth > max_depth or radius < 1:  # Stop if too small (less than 1 pixel)
        return

    # Determine fill color
    fillcolor = 255 if is_white else 0  # 255 = white, 0 = black

    # Draw the current circle
    draw.ellipse(
        [center_x - radius, center_y - radius,
         center_x + radius, center_y + radius],
        fill=fillcolor,
        outline=None
    )

    # If we're at max depth, stop recursing
    if depth >= max_depth:
        return

    # Calculate sizes for top and bottom circles
    top_radius = radius * top_pct
    bottom_radius = radius * bottom_pct

    # Calculate positions for the two main circles
    # Top circle: positioned so it fits in the top portion
    top_center_y = center_y - (radius - top_radius)

    # Bottom circle: positioned so it fits in the bottom portion
    bottom_center_y = center_y + (radius - bottom_radius)

    # Recursively add the pattern inside BOTH the top and bottom circles
    add_recursive_circles(draw, center_x, top_center_y, top_radius,
                         depth + 1, max_depth, not is_white, top_pct, bottom_pct)
    add_recursive_circles(draw, center_x, bottom_center_y, bottom_radius,
                         depth + 1, max_depth, not is_white, top_pct, bottom_pct)

# Streamlit app configuration
st.set_page_config(page_title="Recursive Circles", layout="wide")

st.title("🔄 Recursive Circles Generator")
st.markdown("Create beautiful fractal-like patterns with nested circles")

# Sidebar controls
st.sidebar.header("⚙️ Parameters")

max_depth = st.sidebar.slider(
    "Recursion Depth",
    min_value=5,
    max_value=20,
    value=15,
    step=1,
    help=f"Number of nesting levels. Higher = more detail but slower generation."
)

img_size = st.sidebar.slider(
    "Image Size (pixels)",
    min_value=500,
    max_value=3000,
    value=2000,
    step=100,
    help="Size of the generated image"
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

# Calculate estimated number of circles
estimated_circles = 2 ** max_depth
st.sidebar.info(f"📊 Estimated circles: **{estimated_circles:,}**")

# Generate button
if st.sidebar.button("🎨 Generate Image", type="primary", use_container_width=True):
    with st.spinner(f"Generating {estimated_circles:,} circles..."):
        # Set up the main parameters
        center_x, center_y = img_size // 2, img_size // 2
        main_radius = img_size // 2 - 10  # Leave small margin

        # Create a white background image
        img = Image.new('L', (img_size, img_size), color=255)  # 'L' mode = grayscale
        draw = ImageDraw.Draw(img)

        # Start with selected color
        is_white_start = (start_color == "White")
        add_recursive_circles(draw, center_x, center_y, main_radius, 0, max_depth,
                            is_white_start, top_pct, bottom_pct)

        # Store in session state
        st.session_state['generated_image'] = img
        st.session_state['params'] = {
            'depth': max_depth,
            'size': img_size,
            'top': int(top_pct * 100),
            'bottom': int(bottom_pct * 100),
            'start_color': start_color
        }

    st.success("✅ Image generated!")

# Display the image
if 'generated_image' in st.session_state:
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
        st.metric("Start Color", params['start_color'])

    st.markdown("---")

    # Display image
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.image(st.session_state['generated_image'],
                caption="Click the download button below to save",
                use_container_width=True)

    # Download button
    buf = io.BytesIO()
    st.session_state['generated_image'].save(buf, format='PNG')
    byte_im = buf.getvalue()

    st.download_button(
        label="⬇️ Download Image",
        data=byte_im,
        file_name="recursive_circles.png",
        mime="image/png",
        use_container_width=True
    )
else:
    # Show instructions
    st.info("👈 Adjust the parameters in the sidebar and click **Generate Image** to create your fractal pattern!")

    # Show example
    st.markdown("### Example Pattern")
    st.markdown("""
    This visualization creates a fractal-like pattern where:
    - Each circle is divided into two smaller circles (top and bottom)
    - The pattern repeats recursively inside each circle
    - Colors alternate between black and white at each level
    - The result is a mesmerizing infinite nesting effect
    """)

# Footer
st.markdown("---")
st.markdown("💡 **Tip**: Higher recursion depths create more detailed patterns but take longer to generate. Start with depth 12-15 for good results.")
