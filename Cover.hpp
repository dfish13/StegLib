#pragma once


class Cover {
public:
	virtual unsigned int inject(unsigned char*, unsigned int size) = 0;
	virtual unsigned int extract(unsigned char*, unsigned int size) = 0;
	virtual unsigned int available() = 0;
};

class IntCover : public Cover {
public:

	IntCover() {
		m_size = 0;
		m_data = nullptr;
	}

	IntCover(unsigned int n) {
		m_size = n;
		m_data = new int[n];
	}

	IntCover(const IntCover& ic) {
		m_size = ic.m_size;
		m_data = new int[m_size];
		for (int i = 0; i < m_size; ++i)
			m_data[i] = ic.m_data[i];
	}

	const IntCover& operator=(const IntCover& ic) {
		if (this != &ic) {
			delete[] m_data;
			m_size = ic.m_size;
			m_data = new int[m_size];
			for (int i = 0; i < m_size; ++i)
				m_data[i] = ic.m_data[i];
		}
		return *this;
	}

	~IntCover() {
		delete[] m_data;
	}

	unsigned int inject(unsigned char* buf, unsigned int size) {
		if (size <= available()) {
			m_data[0] = size;
			auto start = (unsigned char*)& m_data[1];
			for (int i = 0; i < size; ++i)
				start[i] = buf[i];
			return size;
		}
		return 0;
	}

	unsigned int extract(unsigned char* buf, unsigned int size) {
		if (m_size > 1 && m_data[0] <= available() && m_data[0] <= size) {
			auto start = (unsigned char*)& m_data[1];
			for (int i = 0; i < m_data[0]; ++i)
				buf[i] = start[i];
			return m_data[0];
		}
		return 0;
	}

	// need 1 int worth of space for the header
	unsigned int available() {
		return (m_size - 1) * sizeof(int);
	}

private:

	int* m_data;
	int m_size;

};