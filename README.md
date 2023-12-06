# world-generator

The World Generator inspired by [Minecraft Earth Map](https://earth.motfe.net/) but runs in parallel.

## Usage

0. Docker is required to run the world generator. Please install Docker first. See [Docker Installation](https://docs.docker.com/get-docker/).
1. Download all the required data. See [Tiles Installation](https://earth.motfe.net/tiles-installation/).Put them all in the `Data` folder and unzip.
2. Download the project Copy the `config.example.yaml` to `config.yaml` and modify the `config.json` to your needs.
3. Run the following command in the project root directory.

```bash
docker pull alicespaceli/trumancrafts_builder
docker run --rm -v $(pwd):/workspace alicespaceli/trumancrafts_builder
```
