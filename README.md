# Stegasaurus 2

### Description

Stegasaurus 2 is a steganography library. Maybe someday it will also be an application which allows non programmers to do steganography. For now though my focus is on making more steganographic methods available so no GUI or web stuff just yet.

### History

The original Stegasaurus was a semester long group project for an undergraduate software engineering course. I was really pleased with what we were able to accomplish, which was basically a web app to show off a neat tool which allowed you to hide information inside PNG images. Our goal was to implement several different methods of steganography and make them available to users, but in the end we were only able to focus on one. Throughout the semester we explored many different possible steganographic methods but they seemed too challenging to take on at the time. Stegasaurus 2 is my attempt to take on those challenges and implement those different methods and some new ones that I have discovered since then.


### Features

At the moment I have 2 main features and of course some smaller tools that I built to help me implement those features.

1. Using LSB substitution to hide data in PNG images.
2. Hiding data in GIF images with a slightly more convoluted method that ultimately uses LSB substitution.
  - Had to build a simple GIF decoder/encoder to manipulate the image data at a low level.
  - Hacked together a way to interface with a C++ implementation of the Blossom V algorithm.




### Future Development

One thing common to all of these methods is that there is some form of header at the beginning of the data that you are extracting from a cover. At the moment I just use a 4 byte header and convert it into an integer which represents the amount of data that follows. It says nothing about the type of data, whether it is a binary file, utf-8 encoded text, zip file, etc. I am thinking about adding a component to the header that indicates what type of data follows so that the responsibility of knowing what form of data is stored is moved into the library and off of the user. This would come at the cost of taking away some potential storage space for hidden data and also would require me to come up with some arbitrary standard. However, this is probably a good idea and should be added.

I am hoping to add JPEG steganography and some audio file steganography. Both of these are going to require some more research before I can move into implementation.
