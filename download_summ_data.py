import logging
from pathlib import Path

from datasets import load_dataset
from tqdm.auto import tqdm
import fire

from billsum_clean import billsum_clean_text
from reddit_tifu_clean import reddit_clean_text

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s -   %(message)s", datefmt="%m/%d/%Y %H:%M:%S", level=logging.INFO
)
logging.getLogger("filelock").setLevel(logging.WARNING)  # prints too many logs


class SummDataset:
    def build(self, save_dir=None, split="train"):
        dataset = self.load(split)

        logger.info(f"Processing {split} data.")
        dataset = dataset.map(self.process)
        self.write_to_disk(dataset, split, save_dir)

    def load(self, split):
        # this will load data for each split, but loading is cheap with datasets, so OKAY!
        return load_dataset(self.dataset, split=self.split_patterns[split])

    def process(self, example):
        raise NotImplementedError()

    def write_to_disk(self, dataset, split, save_dir):
        # to save to val.source, val.target like summary datasets
        src_path = save_dir.joinpath(f"{split}.source")
        tgt_path = save_dir.joinpath(f"{split}.target")
        src_fp = src_path.open("w+")
        tgt_fp = tgt_path.open("w+")

        logger.info(f"Writing {dataset.num_rows} {split} examles at {src_path} and {tgt_path}")
        for example in tqdm(dataset):
            src_fp.write(example["text"] + "\n")
            tgt_fp.write(example["summary"] + "\n")

    @property
    def split_patterns(self):
        return {"train": "train", "val": "validation", "test": "test"}

    @property
    def dataset(self):
        raise NotImplementedError()


class AeslcDataset(SummDataset):
    @property
    def dataset(self):
        return "aeslc"

    def process(self, example):
        example["text"] = example["email_body"].replace("\n", "")
        example["summary"] = example["subject_line"].replace(
            "\n", ""
        )  # subject_line won't have new lines, but still just in case
        return example


class BillSumDataset(SummDataset):
    @property
    def dataset(self):
        return "billsum"

    @property
    def split_patterns(self):
        return {"train": "train[:90%]", "val": "train[90%:]", "test": "test"}

    def process(self, example):
        example["text"] = billsum_clean_text(example["text"])
        example["summary"] = billsum_clean_text(example["summary"])
        return example


class RedditTifuDataset(SummDataset):
    @property
    def dataset(self):
        return "reddit_tifu"

    @property
    def split_patterns(self):
        return {
            "train": "train[:80%]",
            "val": "train[80%:90%]",
            "test": "train[90%:]",
        }

    def load(self, split):
        return load_dataset("reddit_tifu", "long", split=self.split_patterns[split])

    def process(self, example):
        example["text"] = reddit_clean_text(example["documents"])
        example["summary"] = reddit_clean_text(example["tldr"])
        return example


DS_TO_BUILDER = {
    "aeslc": AeslcDataset(),
    "billsum": BillSumDataset(),
    "reddit_tifu": RedditTifuDataset(),
}

SPLITS = ["train", "val", "test"]


def download_summarization_dataset(dataset, save_dir=None, split=None) -> None:
    """Download a dataset using the datasets package and save it to the format expected by finetune.py
    Format of save_dir: train.source, train.target, val.source, val.target, test.source, test.target.
    Args:
        dataset: <str> one of [aeslc, billsum, reddit_tifu]'.
        save_dir: <str>, where to save the datasets, defaults to f'{dataset}'
        split: <str> dataset split. One of [train, val, test]. if None download all splits.
    Usage:
        >>> download_summarization_dataset('aeslc', split='test') # saves to aeslc
    """

    assert dataset in DS_TO_BUILDER.keys()
    if split is not None:
        assert split in SPLITS

    if save_dir is None:
        save_dir = dataset
    save_dir = Path(save_dir)
    save_dir.mkdir(exist_ok=True)

    ds = DS_TO_BUILDER[dataset]
    if split is None:  # all splits
        for split in SPLITS:
            ds.build(save_dir=save_dir, split=split)
    else:
        ds.build(save_dir=save_dir, split=split)

    logger.info(f"Saved {dataset} dataset to {save_dir}.")


if __name__ == "__main__":
    fire.Fire(download_summarization_dataset)
