TARGET=main
CXX=g++
CXXFLAGS=-Wall -std=c++11

main: Main.cpp Cover.hpp Gif.hpp
	$(CXX) -o main $< $(CXXFLAGS)

clean:
	rm main

