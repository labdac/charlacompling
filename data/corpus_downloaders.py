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


class MyProgressBar():
    def __init__(self):
        self.pbar = None
    
    def __call__(self, block_num, block_size, total_size):
        if not self.pbar:
            self.pbar=progressbar.ProgressBar(maxval=total_size)
        downloaded = block_num * block_size
        if downloaded < total_size:
            self.pbar.update(downloaded)
        else:
            self.pbar.finish()

class WikipediaDumpDownloader(CorpusDownloader):
    # https://sites.google.com/site/rmyeid/projects/polyglot#TOC-Download-Wikipedia-Text-Dumps
    def __init__(self, lang, grive_id):
        super().__init__(gdrive_id)
        self.download_path = f"{lang}_wiki_text.tar.lzma"
        self.extract_path = f"{lang}_wiki_text/{lang}/full.txt"

    def download(self, path):
        # Override the path
        path = self.download_path
        os.makedirs(os.path.join(*path.split(os.path.sep)[:-1]), exist_ok=True)
        gdd.download_file_from_google_drive(file_id=self.url,
                                            dest_path=path,
                                            unzip=False,
                                            overwrite=True)
        return self

    def extract(self, path):
        path = self.extract_path
        with lzma.open(self.download_path) as cf:
            os.makedirs(os.path.join(*path.split(os.path.sep)[:-1]), exist_ok=True)
            with open(path, 'w') as of:
                for line in cf:
                    of.write(line.decode('utf-8'))


class WikipediaEsDumpDownloader(WikipediaDumpDownloader):
    def __init__(self):
        super().__init__('es', '0B5lWReQPSvmGOXdCZEZPSnZoYXc')


class WikipediaEnDumpDownloader(WikipediaDumpDownloader):
    def __init__(self):
        super().__init__('en', '0B5lWReQPSvmGOTNxdHo3b0lMc3c')


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
        urllib.request.urlretrieve(self.url, path, MyProgressBar())
        
    def extract(self, path='clean_corpus'):
        os.makedirs(os.path.join(*path.split(os.path.sep)[:-1]), exist_ok=True)
        self._extract_bz2(path)
