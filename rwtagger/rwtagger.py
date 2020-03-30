import argparse
import logging
import pipeline
from pipeline import Pipeline


# call the starting method
if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    help_text = """
    RW-Tagger Script
    This script can the used to annotate textual data with the STWR types 'direct', 'freeIndirect', 
    'indirect' and 'reported'. It can also be used in test mode on annotated data and will then output 
    the evaluation scores. Runs on CPU by default, but can use GPU if flag -gpu is specified.
    
    NOTE: The output directory will be recreated whenever the script is called, i.e. any files already stored in 
        the given output directory will be overwritten!
    
    Examples:
    
    python rwtagger_script.py input_dir output_dir 
    --> simplest call; expects a folder of plain text UTF-8 coded files, outputs tsv files with columns
        for all 4 STWR types
    
    python rwtagger_script.py -gpu -t direct indirect -m test input_dir output_dir 
    --> run the tagger on GPU; annotates the types direct and indirect; runs in test mode (input folder must contain
        annotated data in tsv format; additional score file will be generated and saved in output)
        
    python rwtagger_script.py -gpu -f tsv input_dir output_dir 
    --> run the tagger on GPU (in predict mode for all 4 STWR types); input format is not text but tsv
        
    """
    parser = argparse.ArgumentParser(description=help_text, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("input_dir", help="input directory")
    parser.add_argument("output_dir", help="output directory")
    parser.add_argument("-t", "--rwtypes", help="RW type to annotate: at least one of the following:"
                                               " direct, indirect, reported, freeIndirect; default: all 4 types",
                        default=["direct", "freeIndirect", "indirect", "reported"],
                        nargs="+")
    parser.add_argument("-m", "--mode", help="Mode: predict; test default: predict", default="predict")
    parser.add_argument("-f", "--input_format", help="input_format: either txt or tsv; default: txt", default="txt")
    parser.add_argument("-gpu", "--use_gpu", help="use GPU for processing; if this option is not specified, CPU is used",
                        action="store_true")
    parser.add_argument("-conf", "--conf_vals",
                        help="output confidence values for each annotation",
                        action="store_true")
    args = parser.parse_args()

    pipeline: Pipeline = pipeline.Pipeline(args.use_gpu, logging.INFO)
    # set default value for input chunk_len to 100
    chunk_len = 100
    # check for valid input for input_format
    if args.input_format not in ["tsv", "txt"]:
        print("Unknown input format '{}'. Valid input formats are 'txt' and 'tsv'.".format(args.input_format))
        exit(0)
    # check for valid input for stwr type
    for rw_type in args.rwtypes:
        if rw_type not in ["direct", "indirect", "reported", "freeIndirect"]:
            print("Unknown STWR type '{}'. Valid STWR types are 'direct', 'freeIndirect', 'indirect' and 'reported'.".format(rw_type))
            exit(0)

    if args.mode == "test":
        pipeline.predict(args.input_dir, args.output_dir, args.rwtypes,
                         input_format="tsv", chunk_len=chunk_len, test_scores=True,
                         confidence_vals=args.conf_vals)

    elif args.mode == "predict":
        pipeline.predict(args.input_dir, args.output_dir, args.rwtypes,
                         input_format=args.input_format, chunk_len=chunk_len, test_scores=False,
                         confidence_vals=args.conf_vals)
    else:
        print("Unknown mode. Valid modes are 'predict' and 'test'.")