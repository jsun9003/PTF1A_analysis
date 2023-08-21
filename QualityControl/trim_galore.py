#! /usr/bin/env python3
import argparse
import os
from multiprocessing import Pool
import re
from lxml import etree
import xlwt
parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                 description="""Let's Trim_galore!
Developed from corephi's script of the same name, yet some usages have changed.""")
parser.add_argument("-a", "--args", nargs=1, default=None, help="args used for running trim_galore")
parser.add_argument("-i", "--input", nargs="+", help="input fastq files", required=True)
parser.add_argument("-f", "--fastqc", action='store_true', help="fastqc check the trimmed files")
parser.add_argument("-n", "--no_fastqc", action='store_true', help="skip fastqc pre-check")
parser.add_argument("-o", "--output", nargs=1, default=[os.getcwd()], help="output folder for trimmed reads")
parser.add_argument("-p", "--progress", nargs=1, default=[16], help="progress, default=16", type=int)
parser.add_argument("--phred64", action='store_true', help="use phred64. default = phred33")
args = parser.parse_args()
args_file = args.args
fqs = sorted(args.input)
fastqc = args.fastqc
no_fastqc_pre_check = args.no_fastqc
out_folder = args.output[0]
progress = args.progress[0]
phred = "--phred64" if args.phred64 else "--phred33"

# checking the parameter information
cannot_run_trim = os.system("which trim_galore")
cannot_run_cutadapt = os.system("which cutadapt")
cannot_run_fastqc = os.system("which fastqc")
if cannot_run_trim:
    print("missing trim_galore")
if cannot_run_cutadapt:
    print("missing cutadapt")
if cannot_run_fastqc:
    print("missing fastqc")
try:
    os.mkdir(out_folder)
except FileExistsError:
    pass
raw_fastqc_folder = os.path.join(out_folder, "RawFastQC")
log_folder = os.path.join(out_folder, "logs")
for i in [raw_fastqc_folder, log_folder]:
    try:
        os.mkdir(i)
    except FileExistsError:
        pass

# getting the paired-end or single-end data
fastq_pe = dict()
fastq_se = dict()
for i in fqs:
    pattern = re.compile(r"(([a-zA-Z0-9\-_]+?)[_.]?(R\d[_.])?)(\d)?([_.])?(fastq|fq)([_.]gz)?", re.I)  # must have R*
    if pattern.search(i):
        basename = pattern.search(i).group(1).strip("._")
        mate = pattern.search(i).group(4)
        if mate:
            if basename in fastq_pe.keys():
                fastq_pe[basename] += [i]
            else:
                fastq_pe[basename] = [i]
        else:
            fastq_se[basename] = i
    else:
        print("%s format unsupported" % i)


# fastqc before trim
def run_fastqc(fastq, folder):
    with open(os.path.join(out_folder, "process.log"), "a")as f:
        f.write("fastqc %s\n" % fastq)
    os.system("fastqc %s -o %s >>%s/fastqc.tmp.log" % (fastq, folder, out_folder))


def fastqc_pool(prog, fqs, folder):
    p = Pool(prog)
    for i in fqs:
        p.apply_async(run_fastqc, args=(i, folder))
        print("fastqc %s" % i)
    p.close()
    p.join()


None if no_fastqc_pre_check else fastqc_pool(progress, fqs, raw_fastqc_folder)


# construct general trim parameter
def extract_phred_from_file(file):
    try:
        with open(file)as f:
            source = f.read()
            html = etree.HTML(source.encode("utf-8"))
            encoding = html.xpath("//td[text()='Encoding']/following-sibling::td[1]/text()")[0]
            if re.search(r"Illumina\s+(\S+)$", encoding):
                phred_from_file = "--phred33" if float(re.search(r"Illumina\s+(\S+)$", encoding).group(1)) >= 1.9 else "--phred64"
                if phred_from_file != "--phred33" and phred_from_file != "--phred64":
                    phred_from_file = None
                    print("wrong phred in %s: %s" % (file, phred_from_file))
                else:
                    print("the phred in %s is: %s" % (file, phred_from_file.strip("--")))
                return phred_from_file
            else:
                print("cannot define phred from %s!" % file)
    except Exception as e:
        print(e)
        return None


parameters = dict()
raw_fastqc_file_list = os.listdir(raw_fastqc_folder)
for i in fastq_pe:
    phred_from_file = None
    for fastqc_file in raw_fastqc_file_list:
        if re.search(i, fastqc_file) and re.search(r".*html$", fastqc_file):
            phred_from_file = extract_phred_from_file(os.path.join(raw_fastqc_folder, fastqc_file))
    trim_param = phred_from_file if phred_from_file else phred
    if args_file:
        with open(args_file[0])as f:
            for arg in re.split(r"\s+", f.read().strip()):
                trim_param += " " + arg
    parameters[i] = trim_param + " --paired %s %s" % (fastq_pe[i][0], fastq_pe[i][1])
for i in fastq_se:
    phred_from_file = None
    for fastqc_file in raw_fastqc_file_list:
        if re.search(i, fastqc_file) and re.search(r".*html$", fastqc_file):
            phred_from_file = extract_phred_from_file(os.path.join(raw_fastqc_folder, fastqc_file))
    trim_param = phred_from_file if phred_from_file else phred
    if args_file:
        with open(args_file[0])as f:
            for arg in re.split(r"\s+", f.read().strip()):
                trim_param += " " + arg
    parameters[i] = trim_param + " %s" % (fastq_se[i])


# run trim_galore count with multiple-progress
def run_trim_galore(base_name, parameter):
    with open(os.path.join(out_folder, "process.log"), "a")as f:
        f.write("trimming %s\targs: %s\n" % (base_name, parameter))
    os.system("trim_galore %s -o %s >%s/%s.stdout.log 2> %s/%s.stderr.log" % (
        parameter, out_folder, log_folder, base_name, log_folder, base_name))


def trim_galore_pool(prog):
    p = Pool(prog)
    for i in parameters:
        p.apply_async(run_trim_galore, args=(i, parameters[i]))
    p.close()
    p.join()


trim_galore_pool(progress)

# reformat the files
fastqc_folder = os.path.join(out_folder, "CleanFastQC")
trimed_folder = os.path.join(out_folder, "TrimedReads")
report_folder = os.path.join(out_folder, "Report")
val_folder = os.path.join(out_folder, "ValReads")
for i in [fastqc_folder, trimed_folder, report_folder, val_folder]:
    try:
        os.mkdir(i)
    except FileExistsError as e:
        pass
file_list = os.listdir(out_folder)
val_pattern = re.compile(r"(\S+)_val\S*fq\.gz")
trim_report_pattern = re.compile(r"_trimming_report\.txt")
trimmed_pattern = re.compile(r"(\S+)_trimmed\S*fq\.gz")
for i in file_list:
    a = val_pattern.search(i)
    b = trim_report_pattern.search(i)
    c = trimmed_pattern.search(i)
    if a:
        os.rename(os.path.join(out_folder, i), os.path.join(val_folder, a.group(1) + ".fq.gz"))
    if b:
        os.rename(os.path.join(out_folder, i), os.path.join(report_folder, i))
    elif c:
        os.rename(os.path.join(out_folder, i), os.path.join(trimed_folder, c.group(1) + ".fq.gz"))
if fastqc:
    new_fastqs = [os.path.join(trimed_folder, i) for i in os.listdir(trimed_folder)]
    fastqc_pool(progress, new_fastqs, fastqc_folder)

# summarize the results
x, y = 0, 0
xls = xlwt.Workbook()
sheet = xls.add_sheet('sheet1', cell_overwrite_ok=True)
for i in ["Sample", "AdapterSeq", "AdapterType", "PhreadType", "TotalReads", "AdapterReads", "PassingReads", "TotalBases", "PassingBases"]:
    sheet.write(x, y, i)
    y += 1
x += 1
y = 0
for i in os.listdir(report_folder):
    with open(os.path.join(report_folder, i))as f:
        text = f.read()
        Sample = re.search(r"Input filename: (\S+)\n", text).group(1)
        AdapterSeq = re.search(r"Adapter sequence: '(\S+)'", text).group(1)
        AdapterType = re.search(r"Adapter sequence: '\S+' \((.+)\)", text).group(1)
        PhredType = re.search(r"Quality encoding type selected: (\S+)\n", text).group(1)
        TotalReads = re.sub(",", "", re.search(r"Total reads processed:\s+(.+?)\s", text).group(1))
        AdapterReads = re.sub(",", "", re.search(r"Reads with adapters:\s+(.+?)\s", text).group(1))
        PassingReads = re.sub(",", "", re.search(r"Reads written \(passing filters\):\s+(.+?)\s", text).group(1))
        TotalBases = re.sub(",", "", re.search(r"Total basepairs processed:\s+(.+?)\s", text).group(1))
        PassingBases = re.sub(",", "", re.search(r"Total written \(filtered\):\s+(.+?)\s", text).group(1))
        for i in [Sample, AdapterSeq, AdapterType, PhredType, TotalReads, AdapterReads, PassingReads, TotalBases, PassingBases]:
            sheet.write(x, y, i)
            y += 1
        x += 1
        y = 0
xls.save(os.path.join(out_folder, "Statistics.xls"))
