from pcatool.commonlibs import \
    Path, time, sys, zipfile, \
    urllib, os, shutil, tqdm
from distutils.dir_util import copy_tree
DEFAULT_DATASET = 'diverse_communities_data_excerpts'

def reporthook(count, block_size, total_size):
    global start_time
    if count == 0:
        start_time = time.time() - 1
        return
    duration = time.time() - start_time
    progress_size = int(count * block_size)
    speed = int(progress_size / (1024 * duration))
    progress = int(count * block_size * 100 / total_size)
    percent = min(progress, 100)  # keeps from exceeding 100% for small data
    sys.stdout.flush()
    sys.stdout.write("\r...%d%%, %d KB, %d KB/s, %d seconds elapsed" %
                     (percent, progress_size / 1024, speed, duration))


def error_opening_zip(zip_path):
    try:
        z = zipfile.ZipFile(zip_path)
    except zipfile.BadZipfile:
        return True

    if z.testzip() is not None:
        return True
    return False


def download_data(root: Path, name: Path, download: bool):
    root = root.expanduser()
    if not name.exists():
        print(f"{name} does not exist.")
        zip_path = Path(root.parent, 'data.zip')
        version = "2.2.0"

        version_v = f"v{version}"
        sdnist_version = DEFAULT_DATASET

        download_link = f"https://github.com/usnistgov/SDNist/releases/download/{version_v}/{sdnist_version}.zip"
        if zip_path.exists() and error_opening_zip(zip_path):
            os.remove(zip_path)

        if not zip_path.exists() and download:
            print(f"Downloading all SDNist datasets from: \n"
                  f"{download_link} ...")
            try:
                urllib.request.urlretrieve(
                    download_link,
                    zip_path.as_posix(),
                    reporthook
                )
                print(f'\n Success! Downloaded all datasets to "{root}" directory\n')
            except:
                if zip_path.exists():
                    shutil.rmtree(zip_path)
                raise RuntimeError(f"Unable to download {name}. Try: \n   "
                                   f"- re-running the command, \n   "
                                   f"- downloading manually from {download_link} "
                                   f"and unpack the zip. \n   "
                                   f"- or download the data as part of a release: https://github.com/usnistgov/SDNist/releases\n")

        if zip_path.exists():
            # extract zipfile
            extract_path = Path(root.parent, 'sdnist_data')
            with zipfile.ZipFile(zip_path, 'r') as f:
                for member in tqdm(f.infolist(), desc='Extracting '):
                    try:
                        f.extract(member, extract_path)
                    except zipfile.error as e:
                        raise e
            # delete zipfile
            os.remove(zip_path)
            print()
            copy_from_path = str(Path(extract_path, sdnist_version))
            copy_to_path = str(Path(root))
            print(f"Copying {copy_from_path} to {copy_to_path} ...")
            copy_tree(copy_from_path, copy_to_path)
            shutil.rmtree(extract_path)
        else:
            raise ValueError(f"{name} does not exist.")
