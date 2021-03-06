
class CNN_structure:
    def __init__(self, project_name):
        if project_name == "simulated_data_normal_dist_centers":
            self.set_simulated_data_normal_centers_structure()
        elif project_name == "negative_data_vs_k_shuffle":
            self.set_negative_data_vs_k_shuffle()
        elif project_name == "TF_vs_negative_data":
            self.set_TF_vs_negative_data()
        elif project_name == "TF_vs_k_shuffle":
            self.set_TF_vs_k_shuffle()
        elif project_name == "TF_vs_expanded_negative_data":
            self.set_TF_vs_expanded_negative_data()
        elif project_name == "TF_vs_negative_data_planted_filters":
            self.set_TF_vs_negative_data_planted_filters()
        elif project_name == "H3K27ac_vs_negative_data":
            self.set_H3K27ac_vs_negative_data_structure()
        elif project_name == "H3K27ac_vs_k_shuffle":
            self.set_H3K27ac_vs_k_shuffle()
        elif project_name == "H3K27ac_vs_expanded_negative_data":
            self.set_H3K27ac_vs_expanded_negative_data()
        elif project_name == "H3K27ac_vs_negative_data_planted_filters":
            self.set_H3K27ac_vs_negative_data_planted_filters()
        if len(self.conv_num_kernels) != len(self.conv_shapes):
            print("Error! wrong number of kernels or conv shapes in CNN_structure.py")
            exit(1)
        if len(self.max_pool_shapes) != len(self.conv_shapes):
            print("Error! wrong number of max-pool shapes in CNN_structure.py")
            exit(1)

    def set_TF_vs_k_shuffle(self):
        self.conv_shapes = [[4, 12], [1, 3]]
        self.conv_num_kernels = [7, 50]
        self.max_pool_shapes = [3, 3]
        self.num_conv_layers = len(self.conv_num_kernels)
        self.affine1_size = 20
        self.affine2_size = 20
        self.dropout_prob = 0.9
        self.mini_batch_size = 50

    def set_TF_vs_negative_data(self):
        self.conv_shapes = [[4, 12], [1, 3]]
        self.conv_num_kernels = [7, 50]
        self.max_pool_shapes = [3, 3]
        self.num_conv_layers = len(self.conv_num_kernels)
        self.affine1_size = 20
        self.affine2_size = 20
        self.dropout_prob = 0.9
        self.mini_batch_size = 50

    def set_TF_vs_expanded_negative_data(self):
        self.conv_shapes = [[4, 12], [1, 3]]
        self.conv_num_kernels = [7, 50]
        self.max_pool_shapes = [3, 3]
        self.num_conv_layers = len(self.conv_num_kernels)
        self.affine1_size = 20
        self.affine2_size = 20
        self.dropout_prob = 0.9
        self.mini_batch_size = 50

    def set_TF_vs_negative_data_planted_filters(self):
        self.conv_shapes = [[4, 12], [1, 3]]
        self.conv_num_kernels = [7*4, 50*4]
        self.max_pool_shapes = [3, 3]
        self.num_conv_layers = len(self.conv_num_kernels)
        self.affine1_size = 20
        self.affine2_size = 20
        self.dropout_prob = 0.9
        self.mini_batch_size = 50

    def set_H3K27ac_vs_negative_data_structure(self):
        self.conv_shapes = [[4, 9], [1, 5], [1, 3]]
        self.conv_num_kernels = [20, 30, 40]
        self.max_pool_shapes = [3, 4, 4]
        self.num_conv_layers = len(self.conv_num_kernels)
        self.affine1_size = 90
        self.affine2_size = 45
        self.dropout_prob = 0.85
        self.mini_batch_size = 50

    def set_H3K27ac_vs_negative_data_planted_filters(self):
        self.conv_shapes = [[4, 9], [1, 5], [1, 3]]
        self.conv_num_kernels = [20*4, 30*4, 40*4]
        self.max_pool_shapes = [3, 4, 4]
        self.num_conv_layers = len(self.conv_num_kernels)
        self.affine1_size = 90
        self.affine2_size = 45
        self.dropout_prob = 0.85
        self.mini_batch_size = 50

    def set_H3K27ac_vs_expanded_negative_data(self):
        self.conv_shapes = [[4, 9], [1, 5], [1, 3]]
        self.conv_num_kernels = [20, 30, 40]
        self.max_pool_shapes = [3, 4, 4]
        self.num_conv_layers = len(self.conv_num_kernels)
        self.affine1_size = 90
        self.affine2_size = 45
        self.dropout_prob = 0.85
        self.mini_batch_size = 50

    def set_H3K27ac_vs_k_shuffle(self):
        self.conv_shapes = [[4, 9], [1, 5], [1, 3]]
        self.conv_num_kernels = [20, 30, 40]
        self.max_pool_shapes = [3, 4, 4]
        self.num_conv_layers = len(self.conv_num_kernels)
        self.affine1_size = 90
        self.affine2_size = 45
        self.dropout_prob = 0.85
        self.mini_batch_size = 50

    def set_simulated_data_normal_centers_structure(self):
        self.conv_shapes = [[4, 9], [1, 5], [1, 3]]
        self.conv_num_kernels = [20, 30, 40]
        self.max_pool_shapes = [3, 4, 4]
        self.num_conv_layers = len(self.conv_num_kernels)
        self.affine1_size = 90
        self.affine2_size = 45
        self.dropout_prob = 0.85
        self.mini_batch_size = 50

    def set_negative_data_vs_k_shuffle(self):
        self.conv_shapes = [[4, 9], [1, 5], [1, 3]]
        self.conv_num_kernels = [20, 30, 40]
        self.max_pool_shapes = [3, 4, 4]
        self.num_conv_layers = len(self.conv_num_kernels)
        self.affine1_size = 90
        self.affine2_size = 45
        self.dropout_prob = 0.85
        self.mini_batch_size = 50

    def get_kernels_shape_and_number(self, layer_num):
        return self.conv_shapes[layer_num-1], self.conv_num_kernels[layer_num-1]

    def get_max_pool_kernel_size(self, layer_num):
        return self.max_pool_shapes[layer_num-1]




