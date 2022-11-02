import urllib.request
import progressbar
import tarfile
from google_drive_downloader import GoogleDriveDownloader as gdd
import lzma
import os
import abc


class CorpusDownloader(abc.ABC):
    """ How to use: CorpusDownloader().download().extract() """
    
    def __init__(self, url):
        self.url = url

    @abc.abstractmethod
    def download(self, path):
        pass

    @abc.abstractmethod
    def extract(self, path):
        pass


class MyProgressBar():
    """ Auxiliary class for keeping state of request.urlretrieve """
    def __init__(self):
        self.pbar = None

    def __call__(self, block_num, block_size, total_size):
        if self.pbar is None:
            self.pbar = progressbar.ProgressBar(maxval=total_size)
        
        downloaded = block_num * block_size
        if downloaded < total_size:
            self.pbar.update(downloaded)
        else:
            self.pbar.finish()
            self.pbar = None


class WikipediaDumpDownloader(CorpusDownloader):
    # https://sites.google.com/site/rmyeid/projects/polyglot#TOC-Download-Wikipedia-Text-Dumps
    def __init__(self, lang, gdrive_id):
        super().__init__(gdrive_id)
        self.download_path = f"{lang}_wiki_text.tar.lzma"
        self.extract_path = f"wiki_text/{lang}/full.txt"

    def download(self, path):
        os.makedirs(path, exist_ok=True)
        self.download_path = os.path.join(path, self.download_path)
        gdd.download_file_from_google_drive(file_id=self.url,
                                            dest_path=self.download_path,
                                            unzip=False,
                                            overwrite=True)
        return self

    def extract(self, path='.'):
        self.extract_path = os.path.join(path, self.extract_path)
        os.makedirs(self.extract_path[:-9], exist_ok=True)
        with lzma.open(self.download_path) as cf:
            with open(self.extract_path, 'w') as of:
                for line in cf:
                    of.write(line.decode('latin'))


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

    def download(self, path='.'):
        self.download_path = os.path.join(path, 'clean_corpus.tar.bz2')
        os.makedirs(path, exist_ok=True)
        urllib.request.urlretrieve(
            self.url, self.download_path, MyProgressBar())
        return self

    def extract(self, path='.'):
        self.extract_path = os.path.join(path, 'clean_corpus')
        os.makedirs(path, exist_ok=True)
        with tarfile.open(self.download_path, "r:bz2") as tar:
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner=numeric_owner) 
                
            
            safe_extract(tar, self.extract_path)
