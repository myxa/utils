import os
from collections import defaultdict

import pydicom
import dicom2nifti

DICOM_DIR = r"C:\Users\administrator\Desktop\401_SST_1"      # папка с DICOM
OUTPUT_DIR = r"C:\Users\administrator\Desktop\SST"    # куда сохранять NIfTI

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

if __name__ == "__main__":
# Шаг 1: находим и удаляем неполные временные точки
    removed = find_and_remove_incomplete_timepoints(DICOM_DIR)

