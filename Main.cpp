
#include <iostream>
#include "Gif.hpp"
#include "Cover.hpp"



int main()
{
	IntCover ic(8);

	char greeting[] = "hello";
	unsigned int size = 6;

	char tmp[30];

	std::cout << ic.available() << std::endl;

	std::cout << "return val of inject() = " << ic.inject((unsigned char*)greeting, size) << std::endl;
	std::cout << "return val of extract() = " << ic.extract((unsigned char*)tmp, 30) << std::endl;
	std::cout << tmp << std::endl;

}

