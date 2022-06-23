#include <iostream>
#include <fstream>
#include <string>
#include <stdio.h>
#include <math.h>
#include <filesystem>

#include <opencv2/opencv.hpp>

using namespace std;
using namespace std::filesystem;
using namespace cv;


/*class imgPoint
{
	float x, y, z;
	unsigned char r, g, b;
};*/

const int width = 1280, height = 1024;
const float dynamic_range_max = 900.0;
const float dynamic_range_min = 500.0;
const string dst_dep_ext = "_depth.bmp";
const string dst_gray_ext = "_gray.bmp";

float depth[height][width];

//data one unit struct
struct pixel_unit {
	float x, y, z;
	unsigned char r, g, b;
};

//find depth: one_unit.z and update min_z, max_z
float min_max_unit(float raw_depth, float& min_z, float& max_z) {
	float best_depth;

	best_depth = raw_depth;

	//if best_depth is bigger than dynamic_range_max then set best_depth to dynamic_range_max
	if (raw_depth > dynamic_range_max) {
		best_depth = dynamic_range_max;
		max_z = dynamic_range_max;
	}
	if (best_depth > max_z) {
		max_z = best_depth;
	}

	//if best_depth is smaller than dynamic_range_min then set best_depth to dynamic_range_min
	if (best_depth < dynamic_range_min) {
		best_depth = dynamic_range_min;
		min_z = dynamic_range_min;
	}
	if (best_depth < min_z) {
		min_z = best_depth;
	}
	return best_depth;
}

int main(int argc, char *argv[]){
	int i, j, one_size, pos;
	FILE *fp;
	string org_dir_path, dst_dir_path, org_file_path, dst_dep_file_path, dst_gray_file_path, org_stem_name;
	
	char buf[256];
	
	float min_z, max_z, def_z;
	string line_str;

	struct pixel_unit one_unit;

	Mat dep_img(height, width, CV_8UC1), gray_img(height, width, CV_8UC1);
	vector<int> params{ IMWRITE_PXM_BINARY, 1 };

	if (argc != 3) {
		cout << "command parameters should be 2" << endl;
		cout << "first is org ply img directory, and second is dst dep and gray img directory" << endl;
		return false;
	}

	//check org dir
	if (! exists(argv[1])) {
		cout << "org directory doesn't exist:" << argv[1] << endl;
		return false;
	}

	//check dst dir
	if (! exists(argv[2])) {
		org_dir_path = argv[1];
		dst_dir_path = argv[2];
		create_directory(dst_dir_path);
	}
	else {
		cout << "dst dirctory already existed:" << argv[2] << endl;
		return false;
	}


	for (const directory_entry& x : directory_iterator(org_dir_path)) {
		org_file_path = x.path().string();
		org_stem_name = x.path().stem().string();

		if (fopen_s(&fp, org_file_path.c_str(), "rb") != 0) {
			cout << "Cannot open file:" << org_file_path.c_str() << endl;
			return false;
		}

		line_str = fgets(buf, sizeof(buf), fp);

		while (line_str != "end_header\n") {
			line_str = fgets(buf, sizeof(buf), fp);
			if (line_str == "end_header\n") {
				break;
			}
		}

		one_size = sizeof(float) * 3 + sizeof(unsigned char) * 3;

		min_z = dynamic_range_max;
		max_z = dynamic_range_min;

		pos = 0;

		for (i = 0; i < height; i++) {
			for (j = 0; j < width; j++) {
				if (fread(&one_unit, one_size, 1, fp) < 1) {
					fclose(fp);
					cout << "file read error";
					waitKey();
					return false;
				}
				if (isnan(one_unit.z)) {
					depth[i][j] = 0;
				}
				else {
					depth[i][j] = min_max_unit(one_unit.z, min_z, max_z);
				}
				gray_img.data[pos++] = one_unit.r;
			}
		}
		fclose(fp);

		pos = 0;
		def_z = 255 / (max_z - min_z);
		for (i = 0; i < height; i++) {
			for (j = 0; j < width; j++) {
				if (depth[i][j] == 0.0) {
					dep_img.data[pos] = (unsigned char)0;
				}
				else {
					dep_img.data[pos] = (unsigned char)(255 - (int)((depth[i][j] - min_z) * def_z));
				}
				pos++;
			}
		}

		cout << "max_z:" << max_z << "\tmin_z:" << min_z << endl;

		//display image
		/*imshow("depth", dep_img);
		imshow("gray", gray_img);
		waitKey();*/

		
		dst_dep_file_path = dst_dir_path + "\\" + org_stem_name + dst_dep_ext;
		dst_gray_file_path = dst_dir_path + "\\" + org_stem_name + dst_gray_ext;
		imwrite(dst_dep_file_path, dep_img, params);
		imwrite(dst_gray_file_path, gray_img, params);
	}

}