import urllib.request
import progressbar
import tarfile
from google_drive_downloader import GoogleDriveDownloader as gdd
import lzma
import os
import abc


class CorpusDownloader(abc.ABC):
    # How to use: CorpusDownloader().download().extract()
    def __init__(self, url):
        self.url = url

    @abc.abstractmethod
    def download(self, path):
        pass

    @abc.abstractmethod
    def extract(self, path):
        pass


class WikipediaDumpDownloader(CorpusDownloader):
    # https://sites.google.com/site/rmyeid/projects/polyglot#TOC-Download-Wikipedia-Text-Dumps
    def __init__(self):
        super().__init__('0B5lWReQPSvmGOXdCZEZPSnZoYXc')

    def download(self, path='./es_wiki_text.tar.lzma'):
        self.download_path = path
        os.makedirs(os.path.join(*path.split(os.path.sep)[:-1]), exist_ok=True)
        gdd.download_file_from_google_drive(file_id=self.url,
                                            dest_path=path,
                                            unzip=False, overwrite=True)
        return self

    def extract(self, path='es_wiki_text/es/full.txt'):
        with lzma.open(self.download_path) as cf:
            os.makedirs(os.path.join(*path.split(os.path.sep)[:-1]), exist_ok=True)
            with open(path, 'w') as of:
                for line in cf:
                    of.write(line.decode('utf-8'))


class BillionWordCorpusDownloader(CorpusDownloader):
    # http://crscardellino.github.io/SBWCE/
    def __init__(self):
        super().__init__('http://cs.famaf.unc.edu.ar/~ccardellino/SBWCE/clean_corpus.tar.bz2')

    def _extract_bz2(self, path):
        with tarfile.open(self.download_path, "r:bz2") as tar:
            tar.extractall(path)

    def download(self, path='./clean_corpus.tar.bz2'):
        self.download_path = path
        os.makedirs(os.path.join(*path.split(os.path.sep)[:-1]), exist_ok=True)

        pbar = None
        # https://stackoverflow.com/a/46825841

        def _show_progress(block_num, block_size, total_size):
            global pbar
            if pbar is None:
                pbar = progressbar.ProgressBar(maxval=total_size)

            downloaded = block_num * block_size
            if downloaded < total_size:
                pbar.update(downloaded)
            else:
                pbar.finish()
                pbar = None

        urllib.request.urlretrieve(self.url, path, reporthook=_show_progress)
        return self

    def extract(self, path='clean_corpus'):
        os.makedirs(os.path.join(*path.split(os.path.sep)[:-1]), exist_ok=True)
        self._extract_bz2(path)
