import os
from collections import defaultdict
import pydicom
import subprocess
from pathlib import Path

def group_by_timepoint(datasets):
    """
    Группировка срезов по временной точке.
    Для fMRI/4D MR чаще всего используют (AcquisitionTime, TriggerTime) или TemporalPositionIdentifier.
    Здесь пример с TemporalPositionIdentifier (если он есть).
    """
    groups = defaultdict(list)
    for ds, path in datasets:
        # Берём временной индекс (подстройте под свои данные)
        if "TemporalPositionIdentifier" in ds:
            t = int(ds.TemporalPositionIdentifier)
        elif "AcquisitionTime" in ds:
            t = float(ds.AcquisitionTime)
        else:
            # если нет явного Timepoint – кладём всё в одну группу
            t = 0
        groups[t].append((ds, path))
    return groups

def load_dicom_series(dicom_dir):
    """
    Loads a list of (pydicom Dataset, filepath) tuples from a given directory.

    This function iterates over all files in the given directory, tries to read
    them as DICOM files using pydicom, and appends the resulting
    (Dataset, filepath) tuples to a list.

    If a file cannot be read as a DICOM file (e.g. because it is not
    a valid DICOM file), it is skipped.

    Parameters
    ----------
    dicom_dir : str
        The path to the directory containing the DICOM files

    Returns
    -------
    list
        A list of (pydicom Dataset, filepath) tuples, where each tuple
        contains a Dataset object and the path to the corresponding file.
    """
    datasets = []
    for fname in os.listdir(dicom_dir):
        fpath = os.path.join(dicom_dir, fname)
        if not os.path.isfile(fpath):
            continue
        try:
            ds = pydicom.dcmread(fpath, stop_before_pixels=True)
            datasets.append((ds, fpath))
        except Exception:
            # пропускаем не‑DICOM
            pass
    return datasets

def find_and_remove_incomplete_timepoints(dicom_dir):
    """
    Find and remove incomplete timepoints from a given DICOM directory.

    Incomplete timepoints are those with fewer slices than the maximum number of slices in the given directory.

    :param dicom_dir: The directory containing the DICOM files to process
    :return: A list of paths to files that were removed
    """
    datasets = load_dicom_series(dicom_dir)
    if not datasets:
        print("Нет DICOM‑файлов")
        return

    groups = group_by_timepoint(datasets)

    # Считаем количество срезов в каждом timepoint
    slice_counts = {t: len(files) for t, files in groups.items()}
    print("Срезов в каждом timepoint:", slice_counts)

    # Находим максимальное количество срезов (считаем это «полным» томом)
    max_slices = max(slice_counts.values())

    # Определяем timepoints с меньшим количеством срезов
    incomplete_timepoints = [t for t, n in slice_counts.items() if n < max_slices]
    print("Неполные timepoints:", incomplete_timepoints)

    # Удаляем файлы, относящиеся к неполным timepoints
    removed_files = []
    for t in incomplete_timepoints:
        for ds, path in groups[t]:
            try:
                os.remove(path)
                removed_files.append(path)
            except OSError as e:
                print(f"Не удалось удалить {path}: {e}")

    print(f"Удалено файлов: {len(removed_files)}")
    return removed_files

def run_converter(dicom_dir, out_dir):

    Path(out_dir).mkdir(parents=True, exist_ok=True)

    cmd = [
        "dcm2niix",
        "-b", "y",      # JSON sidecar
        "-z", "y",      # gzip (.nii.gz)
        "-x", "n",      # без реслайсинга
        "-t", "n",
        "-m", "0",
        "-o", out_dir,
        dicom_dir
    ]

    print(" ".join(cmd))
    res = subprocess.run(cmd, capture_output=True, text=True)

    print("STDOUT:\n", res.stdout)
    print("STDERR:\n", res.stderr)

    if res.returncode != 0:
        raise RuntimeError(f"dcm2niix завершился с кодом {res.returncode}")





if __name__ == "__main__":

    DICOM_DIR = r"C:\Users\administrator\Desktop\401_SST_1"      # папка с DICOM
    OUTPUT_DIR = r"C:\Users\administrator\Desktop\SST\test_dicom"    # куда сохранять NIfTI

# Шаг 1: находим и удаляем неполные временные точки
    _ = find_and_remove_incomplete_timepoints(DICOM_DIR)

# Шаг 2: конвертируем DICOM в NIfTI
    run_converter(DICOM_DIR, OUTPUT_DIR)

