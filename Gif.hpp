#include <stdint.h>






class Gif {
public:
	Gif();
	Gif(const char *fname);

private:
	gd_GIF *gif;
};

Gif::Gif() {
	gif = nullptr;
}

Gif::Gif(const char *fname) {
	gif = gd_open_gif(fname);
}