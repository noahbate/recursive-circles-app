# 🔄 Recursive Circles Generator

An interactive Streamlit app that creates beautiful fractal-like patterns with nested circles.

## Features

- **Interactive controls** to adjust recursion depth, image size, and circle proportions
- **Real-time generation** of high-resolution fractal patterns
- **Download capability** to save your creations as PNG files
- **Fast rendering** using PIL for efficient image generation

## How to Use

1. Adjust the sliders in the sidebar:
   - **Recursion Depth**: Control how many layers of nested circles (5-20)
   - **Image Size**: Set the resolution (500-3000 pixels)
   - **Top/Bottom Circle Size**: Customize the proportions
   - **Starting Color**: Choose black or white outer circle

2. Click **Generate Image** to create your pattern

3. Download your creation using the download button

## Local Installation

```bash
pip install -r requirements.txt
streamlit run streamlit_recursive_circles.py
```

## How It Works

The app uses a recursive algorithm to create nested circles:
- Each circle is divided into two smaller circles (top and bottom)
- The pattern repeats inside each circle
- Colors alternate between black and white at each level
- The result is a mesmerizing infinite nesting effect

## Try It Live

[Link to deployed app will go here]
