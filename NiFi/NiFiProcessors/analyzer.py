#!/usr/bin/python3
from ast import literal_eval
import numpy as np
from datetime import datetime
import sys

TOP_THREE = 3

def get_dicts_out_of_data(input_stream):
    """Gets the input stream from NiFi after ingesting the data from influxdb and returns the output as dicts

     Parameters
     ----------
     input_stream : str
         The main stream received from NiFi

     Returns
     -------
     Tuple
        a dictionary for each product organized in tuple data structure
     """
    splitied_data = input_stream.split('}{')
    dict_1 = splitied_data[0] + '}'
    dict_2 = '{' + splitied_data[1]
    dict_1 = literal_eval(dict_1)
    dict_2 = literal_eval(dict_2)

    if list(dict_1.keys())[0] == 'product':
        return dict_1, dict_2
    return dict_2, dict_1


def get_values_per_stream(time_production_list):
    """it will receive a list of tuples (production_out, timestamp) and return just the productions_out

     Parameters
     ----------
     time_production_list : list
         list of tuples (production_out, timestamp)

     Returns
     -------
     list
        the production output per product
     """
    return np.array([ele[1] for ele in time_production_list])


def get_time_per_stream(time_production_list):
    """it will receive a list of tuples (production_out, timestamp) and return just the timestamp

     Parameters
     ----------
     time_production_list : list
         list of tuples (production_out, timestamp)

     Returns
     -------
     list
        the time of production per product
     """
    return np.array([ele[0] for ele in time_production_list])


def normalizer(list_of_products):
    """it will standardize the output with mean zero and std one!

     Parameters
     ----------
     list_of_products : list
         list of values

     Returns
     -------
     list
        normalized list
     """
    std_v = np.std(list_of_products)
    if std_v == 0:
        raise ValueError('Can not divide by zero!')
    return (list_of_products - np.mean(list_of_products)) / (std_v + 0.0000001)


def get_correlation_score(input_stream):
    """it is responsible to find the correlation between the products and the different metrics
      the cross-correlation in 1d has been used to find the correlation score
      if the values close to 1 or -1 this is an indication of high correlation
      if it's close to zero, no correlation between the product and the metrics.

     Parameters
     ----------
     input_stream : string
         a string for the main stream

     Returns
     -------
     Dict
        a dict that contains tuples {"Product_id": (metric_id, correlation_score)}
     """
    correlation_dict = {}
    for key, val in get_dicts_out_of_data(input_stream)[0]['product'].items():
        correlation_list = []
        stream = get_values_per_stream(val)
        for metric, measurements in get_dicts_out_of_data(input_stream)[1]['id'].items():
            np_measurements = get_values_per_stream(measurements)
            min_len = min(len(stream), len(np_measurements))
            correlation_score = np.corrcoef(normalizer(stream[:min_len]), normalizer(np_measurements[:min_len]))
            correlation_list.append((metric, abs(correlation_score[0][1])))
        correlation_dict[key] = correlation_list
    return correlation_dict


def get_top_n(sorted_correlations, n=TOP_THREE):
    """it's responsible for finding the top n parameters

     Parameters
     ----------
     sorted_correlations : list
         list of numerical values
     n : Integer
         Top n parameters to return

     Returns
     -------
     list
        a sorted list of the top n correlations
     """
    return sorted_correlations[-n:][::-1]


def sort_list_tuples_of_correlations(correlations):
    """it will sort a list of tuples based on te second element

     Parameters
     ----------
     correlations : list
         list of numerical values

     Returns
     -------
     list
        a sorted list of the top n correlations
     """
    return sorted(correlations, key=lambda tup: tup[1])


def pretty_get_top_n(top_n_correlated):
    """to report the n top correlated metrics per product

        Parameters
        ----------
        top_n_correlated : list
            list of top n correlated products

        Returns
        -------
        string
           return the n top correlated metrics per product in pretty string :p
        """
    stacked_str = ''
    cnt = 1
    for metric_id, corr_score in top_n_correlated:
        report_top_correlations = f'{cnt}- Parameter ID: {metric_id}, Correlation score: {corr_score}\n'
        stacked_str = stacked_str + report_top_correlations
        cnt += 1
    return stacked_str


def unixtime_to_time(unix_time):
    """Convert the unix time to human-readable time formate

        Parameters
        ----------
        unix_time : integer
            unix time stamp

        Returns
        -------
        string
           return the time with more readable formate
        """
    return datetime.utcfromtimestamp(int(unix_time)).strftime('%H:%M:%S')


def number_of_parameters(input_stream):
    """It will return the number of metrics in a stream

        Parameters
        ----------
        input_stream : str
            the main stream from NiFi

        Returns
        -------
        int
           number of metrics (parameters)
        """
    return len(get_dicts_out_of_data(input_stream)[1]['id'])


def statistical_summary_per_product(input_stream):
    """It will generate a report (basic statistical analysis)

        Parameters
        ----------
        input_stream : str
            the main stream from NiFi

        Returns
        -------
        str
           string contains statistical analysis for the stream
        """
    all_products_info = ''
    for key, val in get_dicts_out_of_data(input_stream)[0]['product'].items():
        stream_values = get_values_per_stream(val)
        stream_diff = np.diff(stream_values)
        production_mean_per_cycle = np.mean(stream_diff)
        production_std_per_cycle = np.std(stream_diff)
        production_max_per_cycle = np.max(stream_diff)
        production_min_per_cycle = np.min(stream_diff)
        production_total = np.max(stream_values)
        stream_time = get_time_per_stream(val)
        stream_time_diff = np.diff(stream_time)
        production_duration = unixtime_to_time(np.max(stream_time) - np.min(stream_time))
        production_start = unixtime_to_time(np.min(stream_time))
        production_ends = unixtime_to_time(np.max(stream_time))
        avg_production_time_per_cycle = unixtime_to_time(np.mean(stream_time_diff))
        max_production_time_per_cycle = unixtime_to_time(np.max(stream_time_diff))
        min_production_time_per_cycle = unixtime_to_time(np.min(stream_time_diff))
        info = f'\nProduct ID: {key}\n' \
               f'- Average production per cycle: {production_mean_per_cycle}\n' \
               f'- Standard deviation of production per cycle: {production_std_per_cycle}\n' \
               f'- Maximum production per cycle: {production_max_per_cycle}\n' \
               f'- Total amount of production: {production_total}\n' \
               f'- Production duration: {production_duration}\n' \
               f'- Production starting time: {production_start}\n' \
               f'- Production ending time: {production_ends}\n' \
               f'- Average time of production per cycle: {avg_production_time_per_cycle}\n' \
               f'- longest duration of production per cycle: {max_production_time_per_cycle}\n' \
               f'- Smallest duration of production per cycle: {min_production_time_per_cycle}\n'
        all_products_info = all_products_info + info
        correlation_info = all_products_info + "\nCorrelation with all parameters:\n" \
                           + generate_correlation_report(input_stream, number_of_parameters(input_stream))
    return correlation_info


def generate_correlation_report(input_stream, top_n_correlated):
    """to report the n top correlated metrics per product

        Parameters
        ----------
        input_stream : str
            the main stream received from NiFi
        top_n_correlated: int
            the top n elements

        Returns
        -------
        string
           return  metrics per product in pretty string
        """
    report_to_send = ''
    for product, correlations in get_correlation_score(input_stream).items():
        report = f'Product ID: {product} \nThe top {top_n_correlated} correlated metrics are:\n' + pretty_get_top_n(
            get_top_n(sort_list_tuples_of_correlations(correlations), top_n_correlated))
        report_to_send = report_to_send + report + '\n'
    return report_to_send


def generate_extended_report(input_stream):
    """generate an extended report about the steam data

        Parameters
        ----------
        input_stream : str
            the main stream received from NiFi

        Returns
        -------
        string
           return  metrics per product in pretty string
        """
    correlation_info = generate_correlation_report(input_stream, TOP_THREE)
    statistical_info = statistical_summary_per_product(input_stream)
    return correlation_info + "\nExtended Report:\n" + statistical_info


if __name__ == 'main':
    input_stream = sys.stdin.read()
    out = generate_extended_report(input_stream)
    sys.stdout.write(out)
