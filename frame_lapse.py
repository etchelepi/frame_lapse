# #############################################################################
# Python Libs needed to make this work
# #############################################################################
import sys
import argparse
import cv2
import numpy as np
import os
import glob
import progressbar
from time import perf_counter 
    
# Default Values
FOURCC_DEFAULT      = cv2.VideoWriter_fourcc(*'mp4v')
EXT_DEFAULT         = ".mp4"

# #############################################################################
def get_input_name(argument):
    if(argument != None): #Check that it's a real arguments
        file_name = argument
    return file_name;
    
# #############################################################################
def get_output_name(argument,modes,force):
    default_base_name   = "output" + str(EXT_DEFAULT)
    ext                 = EXT_DEFAULT
    modes_len           = len(modes)
    if(modes_len < 1):
        print("At Least One Mode needs to be selected")
        exit()
        
    file_name_dict = {
        "rolling_avg": "",
        "rolling_max": "",
        "rolling_median": "",
        "max":""
    }

    if(argument != None): #Check that it's a real arguments
        default_base_name = argument.rsplit( ".", 1 )[ 0 ]
        ext               = "." + str(argument.rsplit( ".", 1 )[ 1 ])
    for index in range(modes_len):
        #Check that we can use it
        if(force):
            temp_file_name = default_base_name + "_" + str(modes[index]) + str(ext)
        else:
            temp_file_name = default_base_name + "_" + str(modes[index]) + str(ext)
            if(os.path.isfile(temp_file_name)):
                num = 0
                while(num < 100):
                    temp_file_name = default_base_name + "_" + str(modes[index]) + "_" + str(num) + str(ext)
                    num = num + 1
                    if(os.path.isfile(temp_file_name) == False):
                        break
        file_name_dict[modes[index]] = temp_file_name
        
    return file_name_dict
# #############################################################################
def get_integer(argument,default):
    result = default
    if(argument != None): #Check that it's a real arguments
        result = int(argument)
    return result;
    
# #############################################################################
def get_float(argument,default):
    result = default
    if(argument != None): #Check that it's a real arguments
        result = float(argument)
    return result;
    
# #############################################################################
def get_frame_length(argument,rate,default):
    result = default
    if(argument != None): #Check that it's a real arguments
        result = int(float(argument) * rate)
    return result;
    
# #############################################################################
def get_sec_frame(argument,rate,default):
    result = default
    if(argument != None): #Check that it's a real arguments
        if( isinstance(argument, float)):
            split_arg = argument.split('.')
            seconds   = int(split_arg[0])
            frames    = int(split_arg[1])
        else:
            seconds   = int(argument)
            frames    = 0
        
        result = int(seconds * rate) + frames
    return result;
# #############################################################################  
def get_fourcc (argument):
    result  = FOURCC_DEFAULT
    if(argument != None): #Check that it's a real arguments
        result  = cv2.VideoWriter_fourcc(*argument)
    return result
# #############################################################################
def get_modes(rolling_avg,rolling_max,rolling_median,max,all):
    modes = []
    
    #Truth Table We Use

    
    if(all == True):
        modes.append("rolling_avg") 
        modes.append("rolling_max") 
        modes.append("rolling_median") 
        modes.append("max") 
        modes_dict = {
            "rolling_avg": True,
            "rolling_max": True,
            "rolling_median": True,
            "max": True
        }    
    else:
        modes_dict = {
            "rolling_avg": rolling_avg,
            "rolling_max": rolling_max,
            "rolling_median": rolling_median,
            "max": max
        }
        if(rolling_avg == True):
            modes.append("rolling_avg") 
        if(rolling_max == True):
            modes.append("rolling_max") 
        if(rolling_median == True):
            modes.append("rolling_median") 
        #Max is fast to compute, so we do it by default
        if(max == True or (rolling_avg == False and rolling_max == False and rolling_median == False)):
            modes.append("max") 
            if((rolling_avg == False and rolling_max == False and rolling_median == False)):
                print("WARNING: No mode Specified. Defaulting to --max")
                modes_dict["max"] = True
                
    return modes_dict,modes

# #############################################################################
# Image Processing Function
# #############################################################################
def ravel(x):
    return x.ravel()
    
    
def sharpen_img(img):
    kernel = (-1/256) * np.array([ [1,4,6,4,1],
                        [4,16,24,16,4],
                        [6,24,-476,24,6],
                        [4,16,24,16,4],
                        [1,4,6,4,1]])
    im = cv2.filter2D(img, -1, kernel)
    return im
    
# #############################################################################
def frame_stack_compute(FRAME_STACK,sharpen,median=False,mean=False,max=False):
    median_img = None
    mean_img = None
    max_img = None
    #Step 1 Make A Stack
    #Y           = np.vstack((x.ravel() for x in FRAME_STACK))
    Y = np.vstack(list(map(ravel, FRAME_STACK)))
    if(median):
        Z           = np.mean(Y,axis = 0)
        median_img  = np.uint8(Z.reshape(FRAME_STACK[0].shape))
        if(sharpen):
            median_img = sharpen_img(median_img)
    if(mean):
        Z           = np.mean(Y,axis = 0)
        mean_img  = np.uint8(Z.reshape(FRAME_STACK[0].shape))
        if(sharpen):
            mean_img = sharpen_img(mean_img)
    if(max):
        Z           = np.amax(Y,axis = 0)
        max_img  = np.uint8(Z.reshape(FRAME_STACK[0].shape))
        if(sharpen):
            max_img = sharpen_img(max_img)
            
    return median_img,mean_img,max_img
    

# ############################################################################# 
def max_composite_compute(PREV_FRAME,NEW_FRAME):
    tmp_stack = []
    tmp_stack.append(PREV_FRAME)
    tmp_stack.append(NEW_FRAME)
    #Y = np.vstack((x.ravel() for x in tmp_stack))
    Y = np.vstack(list(map(ravel, tmp_stack)))
    Z = np.amax(Y,axis = 0)
    composite_frame = np.uint8(Z.reshape(tmp_stack[0].shape))  
    return composite_frame

    
# #############################################################################
def main():
    """ MAIN
    """
    
    #Begin the Argument Handling. This is all the arguments that are supported by this script
    parser = argparse.ArgumentParser()
    parser.add_argument('--input','-i', required=True,                          help='Input File Name')
    parser.add_argument('--frame_avg','-a',                                     help='How Many Frames Make 1 Frame')
    parser.add_argument('--start','-ss',                                        help='How many frames to skip')
    parser.add_argument('--length','-l',                                        help='How long do we want to record for in seconds')
    parser.add_argument('--scale','-s',                                         help='How should we divide the image by')
    parser.add_argument('--frame_rate','-r',                                    help='What is the Rate and which it should be displayed')
    parser.add_argument('--rolling_avg', default=False,action='store_true',     help='Using frame_avg display frames with a mean caculation')
    parser.add_argument('--rolling_max', default=False,action='store_true',     help='Using frame_avg display frames with a MAX caculation')
    parser.add_argument('--rolling_median', default=False,action='store_true',  help='Using frame_avg display frames with a median caculation')
    parser.add_argument('--max', default=False,action='store_true',             help='Just display the max across all frames. This is the fastest option')
    parser.add_argument('--all', default=False,action='store_true',             help='all the modes will be generated')
    parser.add_argument('--overwrite', default=False,action='store_true',       help='Erase the Given Named files')
    parser.add_argument('--sharpen', default=False,action='store_true',         help='Sharpens each frame just a little')
    parser.add_argument('--codec',                                              help='Provide an alterantive 4CC code')
    parser.add_argument('--output','-o',                                        help='Provide a name for the output')
    args = parser.parse_args()
    
    #Begin getting the results and Variables we need from the arguments
    #We need to get all the modes the user is asking for
    FOURCC_SETTING      = get_fourcc (args.codec)
    
    
    MODES_DICT,MODES    = get_modes(args.rolling_avg,args.rolling_max,args.rolling_median,args.max,args.all)
    IN_FILE             = get_input_name(args.input)
    OUT_FILE            = get_output_name(args.output,MODES,args.overwrite)
    NUM_FRAMES          = get_integer(args.length,0)
    FRAME_RATE          = get_integer(args.frame_rate,30)
    NUM_FRAMES_AVG      = get_integer(args.frame_avg,8)
    SCALE               = get_integer(args.scale,3)
    SHARPEN             = args.sharpen
    
    #Do some IO work to confirm the file exists. Get some info about the video
    if(os.path.isfile(IN_FILE)):
        vid_stream  = cv2.VideoCapture(IN_FILE)
        width       = int(vid_stream.get(cv2.CAP_PROP_FRAME_WIDTH))
        height      = int(vid_stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
        length      = int(vid_stream.get(cv2.CAP_PROP_FRAME_COUNT))
        VID_FPS     = vid_stream.get(cv2.CAP_PROP_FPS)
        START       = get_sec_frame(args.start,VID_FPS,0)
        
        if(SCALE == 1):
            if(height < 1920 or width < 1920):
                print("WARNING: This is over 1080p. Please try a smaller scale factor for better performance")
        #Because We can't know how long it was until here we now parse this argument
        # The Length needs to include the start number of frames so we can skip them and get the right length
        # TODO: Account for the Window Size so the length is what the user asks
        LEN         = get_sec_frame(args.length,VID_FPS,length) + START
        out_width   = int(width/SCALE);
        out_height  = int(height/SCALE);
        dim         = (out_width, out_height) 
        pbar        = progressbar.ProgressBar(LEN)
        
        #We need to create all the output Video Streams
        if(MODES_DICT["rolling_avg"]):
            ra_vid_out      = cv2.VideoWriter( OUT_FILE["rolling_avg"], FOURCC_SETTING, FRAME_RATE, (out_width,out_height) ) 
        if(MODES_DICT["rolling_max"]):
            rmax_vid_out    = cv2.VideoWriter( OUT_FILE["rolling_max"], FOURCC_SETTING, FRAME_RATE, (out_width,out_height) ) 
        if(MODES_DICT["rolling_median"]):
            rm_vid_out      = cv2.VideoWriter( OUT_FILE["rolling_median"], FOURCC_SETTING, FRAME_RATE, (out_width,out_height) ) 
        if(MODES_DICT["max"]):
            max_vid_out     = cv2.VideoWriter( OUT_FILE["max"], FOURCC_SETTING, FRAME_RATE, (out_width,out_height) ) 
    else:
        print("%s is not a valid file\n"%(IN_FILE))
    

    FRAME_LIST          = []
    max_bool_start      = True
    #Now read through the video for each frame
    pbar.start()
    t1_start = perf_counter()
    for frames_read in range(LEN):
        ret, full_frame = vid_stream.read()
        #Delay the Start
        if(frames_read >= START):
            if (ret == True):
                pbar.update(frames_read)
                frame = cv2.resize(full_frame, dim, interpolation = cv2.INTER_CUBIC) 
                ###############################################################
                #We need to fill the buffer with Frames
                if(MODES_DICT["rolling_median"] or MODES_DICT["rolling_avg"] or MODES_DICT["rolling_max"]):
                    if(len(FRAME_LIST) < NUM_FRAMES_AVG):
                        FRAME_LIST.append(frame)
                    #otherwise each frame we are going to write out the average
                    else:
                        composite_median,composite_mean,composite_max = frame_stack_compute(FRAME_LIST,SHARPEN, MODES_DICT["rolling_median"], MODES_DICT["rolling_avg"],MODES_DICT["rolling_max"])
                        if(MODES_DICT["rolling_avg"]):
                            ra_vid_out.write( composite_mean.astype(np.uint8) )
                        if(MODES_DICT["rolling_max"]):
                            rmax_vid_out.write( composite_max.astype(np.uint8) )
                        if(MODES_DICT["rolling_median"]):
                            rm_vid_out.write( composite_median.astype(np.uint8) )
                            
                        del FRAME_LIST[0]
                        FRAME_LIST.append(frame)
                ###############################################################
                # The Max Mode doesn't need to care about the rolling average stuff
                if(MODES_DICT["max"]):
                    if(max_bool_start):
                        composite_frame = frame
                        max_bool_start = False
                    else:
                        composite_frame = max_composite_compute(composite_frame,frame)
                        max_vid_out.write(composite_frame.astype(np.uint8))
            ###############################################################
            #We are Out of Frames. If we have a back Catalog lets empty them before stopping
            else:
                left_over = len(FRAME_LIST)
                print("LEFT OVERS: " + str(left_over))
                for frames_read in range(left_over):
                    if(MODES_DICT["rolling_avg"]):
                        ra_vid_out.write( composite_mean.astype(np.uint8) )
                    if(MODES_DICT["rolling_max"]):
                        rmax_vid_out.write( composite_max.astype(np.uint8) )
                    if(MODES_DICT["rolling_median"]):
                        rm_vid_out.write( composite_median.astype(np.uint8) )
                    del FRAME_LIST[0]
                break
        # We are going to quit early when we read some point
        if(LEN != 0):
            if(frames_read == LEN):
                print("WE READ: " + str(frames_read) + " Frames")
                break
        
    t1_stop = perf_counter()
    pbar.finish()
    
    print("File runtime: ", t1_stop-t1_start) 
    
    #Finish our video
    if(MODES_DICT["rolling_avg"]):
        ra_vid_out.release()
    if(MODES_DICT["rolling_max"]):
        rmax_vid_out.release()
    if(MODES_DICT["rolling_median"]):
        rm_vid_out.release()
    if(MODES_DICT["max"]):
        max_vid_out.release()
        
if __name__ == '__main__':
    sys.exit(main())