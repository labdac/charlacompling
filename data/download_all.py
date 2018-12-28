from corpus_downloaders import *
import argparse

AVAILABLE_CORPORA = ['sbwc', 'es_wd', 'en_wd', 'all']

DOWNLOADERS = {
    'sbwc': BillionWordCorpusDownloader(),
    'es_wd': WikipediaEsDumpDownloader(),
    'en_wd': WikipediaEnDumpDownloader()
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Small script to help download corpora used")
    parser.add_argument('--list', '-l', required=False,
                        help="list available corpora",
                        action='store_true')
    parser.add_argument('--download', '-d', required=False,
                        help="download a corpus", default="all")
    args = parser.parse_args()

    if args.list:
        list_ = '\n    '.join(AVAILABLE_CORPORA)
        print(f"Available corpora:{list_}")
        exit(0)

    if args.download == 'all':
        for k, v in DOWNLOADERS.items():
            print(f"Downloading {k}")
            v.download('/tmp').extract()
    else:
        DOWNLOADERS[args.download].download('/tmp').extract()
