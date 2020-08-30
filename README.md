# frame_lapse
*******************************************************************************
Frame Lapse Read Me
*******************************************************************************

This is a basic python script that takes a single video file and then allows 
several simple operations to be done to it and written out as a new video file.

The goal was to take clips of fireflies and try and make them a bit more
interesting to watch. The first version was the max, which i still feel makes
the best results for fireflies.

The arguments of the script are as follows:


--input             :   This is the only required argument. 
                        A video file must be provided. 
                    
--frame_avg         :   This is the size of the window on which the operations
                        for all the rolling calculations are done. Larger windows
                        dramatically slow down runtime. Each frame requires the
                        entire window of images to be operated upon.
--start             :   This is when to start the video. It uses a <Second>.<Frame>
                        format. Where whole numbers are seconds, and anything after
                        the decimal is a frame. Any number of frames can be 
                        specified. 0.48 and 2 are the same for 24fps video
--length            :   This is how long after the start to run for. It also uses the
                        <Second>.<Frame> format. If it's longer then the video it
                        will stop at the end.
--scale             :   This is an integer to scale the image. 1 is full size. 2 is
                        is half. The larger the number the faster the processing.
                        It's done as the first step and dramatically reduces data
                        needed to be processed.
                        DO NOT USE IT FOR SCALNING. Use it to preview. Then export
                        at a larger or equal size of your target and scale it with
                        ffmpeg or some other software.
--frame_rate        :   This is the frame rate of the output file. It can be faster
                        or slower then the input. No audio is preserved so no
                        sync issues. For example you can take a 30p video and 
                        target 60 and end up with a shorter video, or 24 and
                        a longer video. THe number of frames should be the same
                        as specified by --length
--rolling_avg       :   If this flag is used the window generates a frame using a 
                        mean calculation.
--rolling_max       :   This Video output mode outputs a frame with the max value
                        of each image in the window.
--rolling_median    :   This video output mode outputs a frame based on the median
                        value across the entire window
--max               :   This is the Default if nothing is specified. It outputs
                        a video where each frame represents the max value of every
                        frame before it. This is the fastest choice. It also does
                        not use the --frame_avg value. It works best for tripod
                        mounted video for short durations. Eventually it will turn
                        white on a long enough clip
--all               :   All the video outputs can be run in any combination. Each
                        gets it's own output. -all does them with a single flag
                        instead of needing to call them one by one.
--overwrite         :   Replace the files, otherwise it adds a number to the out
                        name. By default it will not overwrite.
--sharpen           :   Especially with the Median and Mean, the video becomes
                        a little softer. This will apply a medium strength sharpen
                        filter. It will slow down the runtime. But it's only done
                        on the result frame, so it's minimal compared to 
                        frame avg on performance.
--codec             :   The default codec is mp4v with .mp4 extension. Depending
                        on what is desired, you can provide a FourCC code for
                        a different video file. Some codecs need a different 
                        extension to work. Specify that with the output flag
--output            :   This lets a user choose an output name. The name is
                        not EXACTLY the same. Please also provide an extension.
                        It will split the name <name>.<ext> and then insert the
                        video type eg: <name>_max_<num>.<ext> 
                        the default will be like "output_max.mp4"
                        
There is no Multi-threading support right now. There is no multi file input support.
It only takes video inputs

These shouldn't be hard to change if needed. But this is more for fun then trying to
produce quality effects.

Some Example Commands:

The image here is a 4k30p clip



Rolling MAX:

Output a 1080p Motion Jpeg version of the clip, at 24fps using 45 seconds of the in clip, starting 1 seconds
into it, and average 48 frames together for each result frame and name it result.avi

>frame_lapse.py -i <filename>.MP4 -ss 1 -l 45 -r 24 --rolling_max  -a 48 -s 2 -o result.avi --codec MJPG

result: result_rolling_max.avi running 54 seconds (107MB) taking 682 seconds to generate




MAX:

Generate a mp4 720p60 image using 45 seconds of the original clip starting 2 second in and give it the 
default output name.


> frame_lapse.py -i <filename>.MP4 -ss 1 -l 45 -r 60 --max -s 3

Result: output_max.mp4 running 22 seconds (6MB) Taking 51 seconds



Rolling MEAN (Rolling Avg):

generate a 1080p30 video using 10 seconds of the original clip starting 1 second in, and let it use a custom name

>frame_lapse.py -i <filename>.MP4 --start 1 --length 10 --frame_avg 15 --scale 2 --rolling_avg --codec MJPG --output result.avi

Result: result_rolling_avg.avi running for 9 seconds and 15 frames at 1080p. The rolling window ate 15 frames before it started to output. Add an extra 15 frames to the --length tag to correct: 10.15



Rolling MEDIAN:

>frame_lapse.py -i <filename>.MP4 --start 1 --length 10 --frame_avg 15 --scale 1 --rolling_median --codec MJPG --output result.avi

Result: result_rolling_median.avi running for 9 seconds and 15 frames at 1080p. The rolling window ate 15 frames before it started to output. Add an extra 15 frames to the --length tag to correct: 10.15

Final comments:

This is a pretty basic script. It might be useful to someone who doesn't know python but wishes to do something interesting with averaging video together. Or it might be a helpful reference to see how it works in python.
