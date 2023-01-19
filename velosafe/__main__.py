import click

from velosafe.data import Datasets, get_training_data


@click.group()
def cli():
    pass


@cli.command()
@click.argument(
    "dataset",
    type=click.Choice(["accidents", "all"] + [x for x in vars(Datasets).keys() if not x.startswith("__")]),
    required=True,
)
@click.argument("path", type=click.Path(), required=False, default="./data")
def download(dataset, path):
    if dataset == "accidents":
        datasets = [
            Datasets.ACCIDENTS_VEHICULES,
            Datasets.ACCIDENTS_PLACES,
            Datasets.ACCIDENTS_USERS,
            Datasets.ACCIDENTS_CHARACTERISTICS,
        ]
    elif dataset == "all":
        datasets = (v for k, v in vars(Datasets).items() if not k.startswith("__"))
    else:
        datasets = [getattr(Datasets, dataset)]

    for dataset in datasets:
        click.echo(f"Downloading {dataset.filename}.")
        dataset.download(path)
    click.echo("All done 🎉")


@cli.command()
@click.argument("path", type=click.Path(), required=False, default="./data")
def datagen(path):
    get_training_data(data_folder=path)
    click.echo("All done 🎉")


if __name__ == "__main__":
    cli()
