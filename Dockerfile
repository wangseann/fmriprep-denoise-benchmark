FROM python:3.10-slim

# Set up working directory
WORKDIR /home/seann/scratch/denoise/fmriprep-denoise-benchmark/

# Copy everything into the image
COPY . /opt/bids_app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set entrypoint for BIDS App CLI
ENTRYPOINT ["python", "cli.py"]