import tensorflow as tf
from time import gmtime, strftime
import os
import subprocess
import random
import string
import numpy as np
import layer_defs as ld
import data_handle as dh
from DataSetObject import DataSetObject



MAXIMAL_K = 9
samples_k_lets_dirs = output_k_lets_dirs = ["preserving_"+str(k)+"-let_counts/" for k in range(1, MAXIMAL_K+1)]


class CNN:
    LOSS_EPSILON = 0.01
    # ACCURACY_EPSILON = 0.0001

    def __init__(self, project, num_epochs, num_runs, species_to_train_on=None, k=None, n=None,
                 init_according_to_given_filters=False, init_model_ids=None):
        self.project = project
        self.num_epochs = num_epochs
        self.NUM_RUNS = num_runs  # the final accuracy is the max accuracy of the {self.NUM_RUNS} runs
        self.k = k
        print("self.k = ", self.k)
        self.species_to_train_on = species_to_train_on
        print("self.species_to_train_on = ", self.species_to_train_on)
        self.n = n
        self.project.num_times_negative_data_is_taken = self.n
        self.init_according_to_given_filters = init_according_to_given_filters
        self.init_model_ids = init_model_ids

    def inference(self, seqs_placeholder, keep_prob_placeholder):
            """"
            defines the model's architecture - from input (placeholder) to output
            """
            x = tf.reshape(seqs_placeholder, shape=[-1, 4, dh.SAMPLE_LENGTH, 1])
            kernel_shape, num_kernels = self.project.CNN_structure.get_kernels_shape_and_number(1)
            max_pool_kernel_size = self.project.CNN_structure.get_max_pool_kernel_size(1)
            # in first convolutional layer - make a special conv function,
            # that takes maximum over forward and reverse-complement form of each filter.
            conv = ld.conv_max_forward_reverse("conv1", x, num_kernels, kernel_shape, self.project,
                                               init_according_to_given_filters=self.init_according_to_given_filters,
                                               init_model_ids=self.init_model_ids)
            max_pool = tf.nn.max_pool(conv, ksize=[1, 1, max_pool_kernel_size, 1],
                                      strides=[1, 1, max_pool_kernel_size, 1], padding='VALID')
            x = max_pool
            for conv_layer_num in range(2, self.project.CNN_structure.num_conv_layers+1):
                kernel_shape, num_kernels = \
                    self.project.CNN_structure.get_kernels_shape_and_number(conv_layer_num)
                max_pool_kernel_size = self.project.CNN_structure.get_max_pool_kernel_size(conv_layer_num)
                conv = ld.conv("conv"+str(conv_layer_num), x, num_kernels, kernel_shape, self.project,
                               init_according_to_given_filters=self.init_according_to_given_filters,
                               init_model_ids=self.init_model_ids)
                max_pool = tf.nn.max_pool(conv, ksize=[1, 1, max_pool_kernel_size, 1],
                                          strides=[1, 1, max_pool_kernel_size, 1], padding='VALID')

            conv_flat = ld.flatten(max_pool)
            # Computes dropout
            # With probability keep_prob, outputs the input element scaled up by 1 / keep_prob,
            # otherwise outputs 0. The scaling is so that the expected sum is unchanged.
            conv_flat_drop = tf.nn.dropout(conv_flat, keep_prob_placeholder)
            # two affine (fully-connected) layers
            aff1 = ld.affine("local3", conv_flat_drop, self.project.CNN_structure.affine1_size)
            aff2 = ld.affine("local4", aff1, self.project.CNN_structure.affine2_size)
            # output layer -
            # softmax linear layer: An affine layer (fully connected) with 2 possible outputs: True/False.
            aff2 = ld.affine("softmax_linear", aff2, 2, False)
            y = tf.nn.softmax(aff2, name="output")
            #########################################################################
            # from paz:
            # dense1 = tf.layers.dense(conv3_flat, dense1_cfg["size"], activation=tf.nn.relu, name="dense1")
            # # dropout = tf.nn.dropout(dense1, keep_prob=dropout_keep_prob)
            #
            # dense2 = tf.layers.dense(dense1, dense2_cfg["size"], activation=tf.nn.relu, name="dense2")
            # # output layer
            # dense_out = tf.layers.dense(dense2, general_cfg["num_outs"], activation=None, name="dense_out")
            # # we're returning the unscaled output so we can use the safe: tf.nn.softmax_cross_entropy_with_logits
            # return dense_out
            #########################################################################
            return y

    def save_model(sess, model_id, checkpoints_folder):
        """
        A static method
        :param model_id:
        :param checkpoints_folder:
        :return:
        """
        saver = tf.train.Saver()
        saver.save(sess, os.path.join(checkpoints_folder, model_id))

        tar_path = os.path.join(checkpoints_folder, model_id) + '.tar'
        subprocess.call(['tar', 'jcvf', tar_path, "-C", checkpoints_folder,
                         model_id + '.index',
                         model_id + '.data-00000-of-00001',
                         model_id + '.meta',
                         '--remove-files'])
        return model_id

    def uid(self):
        model_id = strftime("%Y%m%d%H%M%S") + "." + ''.join(
            [random.choice(string.ascii_letters + string.digits) for _ in range(8)])
        if self.species_to_train_on is not None:
            print("self.species_to_train_on = ", self.species_to_train_on)
            species_name = self.project.species[self.species_to_train_on]
            print("species_name = ", species_name)
        else:
            species_name = "simulated"
        print("train on:", species_name)
        if self.project.k:
            model_id_result = species_name + "_k_" + str(self.project.k) + "_" + model_id
        elif self.project.sigma:
            model_id_result = species_name + "_normal_sigma_" + str(self.project.sigma) + "_" + model_id
        elif self.n is not None:
            model_id_result = species_name + "_n_" + str(self.n) + "_" + model_id
        else:
            model_id_result = species_name + "_" + model_id

        return model_id_result

    def evaluate(self):
        self.project.num_times_negative_data_is_taken = self.n
        # generate a placeholder for sequences
        x_in = tf.placeholder(tf.float32, [None, 4, dh.SAMPLE_LENGTH], name="input_x")
        # dropout rate
        keep_prob = tf.placeholder(tf.float32, name="input_keep_prob")
        # correct labels
        y_in = tf.placeholder(tf.float32, [None, 2], name="input_y")
        # Build a Graph that computes predictions from the inference model
        y = self.inference(x_in, keep_prob)
        # loss functions (cross-entropy)
        cross_entropy_loss = tf.reduce_mean(-tf.reduce_sum(y_in * tf.log(y), axis=1))
        # cross_entropy_loss = tf.losses.sigmoid_cross_entropy(multi_class_labels=y_in,
        #                                                      logits=y)
        train_step = tf.train.AdamOptimizer().minimize(cross_entropy_loss)
        correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_in, 1))
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
        tf.summary.scalar("validation accuracy", accuracy)
        index_to_train_on = self.species_to_train_on
        if self.n is not None:
            species_dir = os.path.join(self.project.base_dir_data_path,
                                       str(self.n)+"_times_negative_data",
                                        "npy_files",
                                        self.project.species[index_to_train_on])
            train_x_path = os.path.join(species_dir, 'train_X.npy')
            train_y_path = os.path.join(species_dir, 'train_Y.npy')
            validation_x_path = os.path.join(species_dir, 'validation_X.npy')
            validation_y_path = os.path.join(species_dir, 'validation_Y.npy')
        elif self.project.species != ["simulated"]:
            if self.k is None:
                train_x_path = os.path.join(self.project.samples_base_dir,
                                            self.project.species[index_to_train_on], 'train_X.npy')
                train_y_path = os.path.join(self.project.samples_base_dir,
                                            self.project.species[index_to_train_on], 'train_Y.npy')
                validation_x_path = os.path.join(self.project.samples_base_dir,
                                                 self.project.species[index_to_train_on],
                                                 'validation_X.npy')
                validation_y_path = os.path.join(self.project.samples_base_dir,
                                                 self.project.species[index_to_train_on],
                                                 'validation_Y.npy')
            else:
                train_x_path = os.path.join(self.project.samples_base_dir, self.project.species[index_to_train_on],
                                            samples_k_lets_dirs[self.k - 1], 'train_X.npy')
                train_y_path = os.path.join(self.project.samples_base_dir, self.project.species[index_to_train_on],
                                            samples_k_lets_dirs[self.k - 1], 'train_Y.npy')
                validation_x_path = os.path.join(self.project.samples_base_dir, self.project.species[index_to_train_on],
                                                 samples_k_lets_dirs[self.k - 1], 'validation_X.npy')
                validation_y_path = os.path.join(self.project.samples_base_dir, self.project.species[index_to_train_on],
                                                 samples_k_lets_dirs[self.k - 1], 'validation_Y.npy')
        else:  # simulated data
            train_x_path = os.path.join(self.project.samples_base_dir, 'train_X.npy')
            train_y_path = os.path.join(self.project.samples_base_dir, 'train_Y.npy')
            validation_x_path = os.path.join(self.project.samples_base_dir, 'validation_X.npy')
            validation_y_path = os.path.join(self.project.samples_base_dir, 'validation_Y.npy')

        train_set = DataSetObject(train_x_path, train_y_path, self.num_epochs)
        validation_set = DataSetObject(validation_x_path, validation_y_path, self.num_epochs)
        merged_summary_op = tf.summary.merge_all()

        validation_batch = validation_set.get_next_batch(self.project.CNN_structure.mini_batch_size)
        validation_batch_samples, validation_batch_labels = validation_set.get_samples_labels(validation_batch)

        best_run_validation_index = -1
        best_model_validation_id = -1
        # the final accuracy will be the max accuracy of the {self.NUM_RUNS} runs
        max_validation_accuracy = -1
        with tf.Session() as sess:
            stop = False
            for num_run in range(self.NUM_RUNS):
                print("start run #", num_run+1)
                train_set.initialize_epoch_and_position()
                validation_set.initialize_epoch_and_position()
                # skip_run = False
                # prev_validation_accuracy = 1
                model_id = self.uid()
                print("Training model: " + model_id)
                board_path = os.path.join(self.project.board_folder,  model_id)
                summary_writer = tf.summary.FileWriter(board_path, sess.graph)
                sess.run(tf.global_variables_initializer())
                # print("before iterations: train_set.get_current_epoch() = ", train_set.get_current_epoch())
                # print("before iterations: train_set.get_current_position_in_epoch() = ", train_set.get_current_position_in_epoch())
                # print("train_set.get_num_samples() = ", train_set.get_num_samples())
                # print("train_set.get_num_samples() % self.mini_batch_size = ",train_set.get_num_samples() % self.mini_batch_size)
                num_iterations_in_one_epoch = int(train_set.get_num_samples() / self.project.CNN_structure.mini_batch_size) + \
                                   (train_set.get_num_samples() % self.project.CNN_structure.mini_batch_size)
                print("num_iterations_in_one_epoch = ", num_iterations_in_one_epoch)
                step = 0
                for i in range(num_iterations_in_one_epoch * self.num_epochs):
                    # if skip_run:
                    #     break
                    step += 1
                    train_batch = train_set.get_next_batch(self.project.CNN_structure.mini_batch_size)
                    train_batch_samples, train_batch_labels = train_set.get_samples_labels(train_batch)

                    summary_str, _, loss = sess.run([merged_summary_op, train_step, cross_entropy_loss],
                                                 feed_dict={x_in: train_batch_samples,
                                                            y_in: train_batch_labels,
                                                            keep_prob: 1.0})
                    summary_writer.add_summary(summary_str, i)
                    summary_writer.flush()
                    loss_sum = np.sum(loss)
                    # skip to next epoch if loss is very small:
                    if loss_sum < self.LOSS_EPSILON:
                        print('loss < '+str(self.LOSS_EPSILON)+', skipping to next run.')
                        curr_epoch = train_set.get_current_epoch()
                        while curr_epoch == train_set.get_current_epoch():
                            train_set.get_next_batch(self.project.CNN_structure.mini_batch_size)
                            step += 1
                        # skip_run = True
                        # prev_validation_accuracy = validation_accuracy
                        break
                    if (step+1) % (4*self.project.CNN_structure.mini_batch_size) == 0:
                        train_accuracy = accuracy.eval(feed_dict={x_in: train_batch_samples,
                                                                  y_in: train_batch_labels,
                                                                  keep_prob: 1.0})
                        validation_accuracy = accuracy.eval(feed_dict={x_in: validation_batch_samples,
                                                                       y_in: validation_batch_labels,
                                                                       keep_prob: 1.0})
                        time_str = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                        # if train_set.get_current_position_in_epoch() > (num_iterations_in_one_epoch * (self.num_epochs-1)):
                        print("{0} - epoch {1}, training accuracy: {2:.3f}, "
                          "validation accuracy: {3:.3f}".format(time_str,
                                                                train_set.get_current_epoch(),
                                                                train_accuracy,
                                                                validation_accuracy))
                        # TODO delete:
                        # if 0.71 < validation_accuracy < 0.76:
                        #     max_validation_accuracy = -1
                        #     stop = True
                        #     break

                        # if abs(validation_accuracy - prev_validation_accuracy) < EPSILON:
                        #     print('validation_accuracy is not getting better. '
                        #           'skipping to next epoch...')
                        #     curr_epoch = train_set.get_current_epoch()
                        #     while curr_epoch == train_set.get_current_epoch():
                        #         train_set.get_next_batch(self.mini_batch_size)
                        #     prev_validation_accuracy = validation_accuracy
                        #     break
                        # prev_validation_accuracy = validation_accuracy
                        # if self.project.project_name == "H3K27ac_vs_negative_data":
                        #     if train_set.get_current_epoch() > 6 and validation_accuracy < 0.6:
                        #         print('validation_accuracy is small. '
                        #               'skipping to next run...')
                        #         # skip_run = True
                        #         break


                        # if self.project.project_name == "simulated_data":
                        #     if train_set.get_current_epoch() > 10 and validation_accuracy < 0.6:
                        #         print('validation_accuracy is small. '
                        #               'skipping to next run...')
                        #         # skip_run = True
                        #         break

                            # print("before train_step.run")
                            # train_step.run(feed_dict={x_in: train_batch_samples,
                            #                           y_in: train_batch_labels,
                            #                           keep_prob: self.project.dropout_prob})
                # save the trained model if its better than before:
                if validation_accuracy > max_validation_accuracy:
                    max_validation_accuracy = validation_accuracy

                    if best_model_validation_id != -1:
                        os.remove(os.path.join(self.project.checkpoints_folder, best_model_validation_id+'.tar'))
                    best_model_validation_id = model_id
                    best_run_validation_index = num_run
                    # save the best model in a different folder:
                    CNN.save_model(sess, model_id, self.project.checkpoints_folder)
                    if stop:
                        break # TODO delete
        tf.reset_default_graph()
        return max_validation_accuracy, best_model_validation_id, best_run_validation_index


