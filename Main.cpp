// Stegasaurus.cpp : This file contains the 'main' function. Program execution begins and ends there.
//

#include <iostream>
#include "Cover.h"


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

// Run program: Ctrl + F5 or Debug > Start Without Debugging menu
// Debug program: F5 or Debug > Start Debugging menu

// Tips for Getting Started: 
//   1. Use the Solution Explorer window to add/manage files
//   2. Use the Team Explorer window to connect to source control
//   3. Use the Output window to see build output and other messages
//   4. Use the Error List window to view errors
//   5. Go to Project > Add New Item to create new code files, or Project > Add Existing Item to add existing code files to the project
//   6. In the future, to open this project again, go to File > Open > Project and select the .sln file
