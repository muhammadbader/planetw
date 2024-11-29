# Base image
FROM python:3.9

# Install required pip libraries
RUN pip install --no-cache-dir numpy pandas requests geopandas shapely

# Set working directory (optional)
WORKDIR /scripts

# Copy dummy script (optional)
# COPY dummy.py /scripts/

# Default command (optional)
CMD ["python"]

