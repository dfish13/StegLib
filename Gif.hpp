#include <stdint.h>
#include <stdio.h>



class Gif {
public:
	Gif();
	Gif(const char *fname);

private:
	FILE *gif;
};

Gif::Gif() {
	gif = nullptr;
}

Gif::Gif(const char *fname) {
	gif = fopen(fname, "r");
}
