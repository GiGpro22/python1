import random
import multiprocessing
import threading
import time
import os
import psutil
from datetime import datetime

def get_cpu_load():
    return psutil.cpu_percent(interval=1)

def get_available_processes():
    cpu_load = get_cpu_load()
    logical_cores = os.cpu_count()
    available_cores = max(1, logical_cores - int(logical_cores * cpu_load / 100))
    return available_cores

def log_message(message, log_queue=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    log_entry = f"[{timestamp}] {message}"
    
    if log_queue:
        log_queue.put(log_entry)
    else:
        print(log_entry)

def generate_matrix(rows, cols):
    return [[random.randint(1, 100) for _ in range(cols)] for _ in range(rows)]

def save_partial_result(result_part, filename_prefix, process_id, thread_id, log_queue):
    try:
        filename = f"{filename_prefix}_proc{process_id}_thread{thread_id}.txt"
        with open(filename, 'w') as f:
            for row in result_part:
                f.write(' '.join(map(str, row)) + '\n')
        log_message(f"Process {process_id}, thread {thread_id} saved partial result to {filename}", log_queue)
    except Exception as e:
        log_message(f"Error saving partial result: {str(e)}", log_queue)

def multiply_partial(matrix_a, matrix_b, start_row, end_row, process_id, log_queue, result_queue):
    result_part = []
    saver_threads = []
    
    for i in range(start_row, end_row):
        row_result = []
        for j in range(len(matrix_b[0])):
            element = sum(matrix_a[i][k] * matrix_b[k][j] for k in range(len(matrix_a[0])))
            row_result.append(element)
        result_part.append(row_result)
        
        # Периодически сохраняем промежуточные результаты в потоках
        if i % max(1, (end_row - start_row) // 5) == 0:  
            thread_id = len(saver_threads)
            t = threading.Thread(
                target=save_partial_result,
                args=(result_part, "partial_result", process_id, thread_id, log_queue)
            )
            t.daemon = True
            t.start()
            saver_threads.append(t)
    
    # завершения всех потоков сохранения
    for t in saver_threads:
        t.join()
    
    result_queue.put((start_row, end_row, result_part))
    log_message(f"Process {process_id} finished rows {start_row}-{end_row-1}", log_queue)

def combine_results(result_parts, total_rows, total_cols):
    result = [[0] * total_cols for _ in range(total_rows)]
    for start_row, end_row, part in result_parts:
        for i in range(start_row, end_row):
            result[i] = part[i - start_row]
    return result

def logger_process(log_queue, stop_event):
    with open("matrix_multiplication.log", "a") as log_file:
        while not stop_event.is_set() or not log_queue.empty():
            try:
                log_entry = log_queue.get(timeout=1)
                print(log_entry)  # Вывод в консоль
                log_file.write(log_entry + "\n")
                log_file.flush()
            except:
                pass

def main():
    # Инициализация логгирования
    log_queue = multiprocessing.Queue()
    stop_logging_event = multiprocessing.Event()
    logger = multiprocessing.Process(
        target=logger_process,
        args=(log_queue, stop_logging_event)
    )
    logger.start()
    
    log_message("Program started", log_queue)
    
    try:
        # Ввод размеров матриц
        while True:
            try:
                a_rows = int(input("Введите количество строк первой матрицы: "))
                a_cols = int(input("Введите количество столбцов первой матрицы: "))
                b_rows = int(input("Введите количество строк второй матрицы: "))
                b_cols = int(input("Введите количество столбцов второй матрицы: "))
                
                if a_cols != b_rows:
                    print("Ошибка: Количество столбцов первой матрицы должно быть равно количеству строк второй матрицы!")
                    continue
                break
            except ValueError:
                print("Ошибка: Введите целые числа!")
        
        # Определение доступного количества процессов
        max_processes = get_available_processes()
        log_message(f"Available CPU cores: {os.cpu_count()}, CPU load: {get_cpu_load()}%, Max available processes: {max_processes}", log_queue)
        
        while True:
            try:
                num_processes = int(input(f"Введите количество процессов для умножения (1-{max_processes}): "))
                if 1 <= num_processes <= max_processes:
                    break
                print(f"Ошибка: Введите число от 1 до {max_processes}!")
            except ValueError:
                print("Ошибка: Введите целое число!")
        
        # Генерация матриц
        log_message("Generating matrices...", log_queue)
        matrix_a = generate_matrix(a_rows, a_cols)
        matrix_b = generate_matrix(b_rows, b_cols)
        
        log_message(f"Matrix A ({a_rows}x{a_cols}):\n{matrix_a}", log_queue)
        log_message(f"Matrix B ({b_rows}x{b_cols}):\n{matrix_b}", log_queue)
        
        # Распределение строк между процессами
        rows_per_process = a_rows // num_processes
        extra_rows = a_rows % num_processes
        
        result_queue = multiprocessing.Queue()
        processes = []
        
        log_message(f"Starting matrix multiplication with {num_processes} processes...", log_queue)
        start_time = time.time()
        
        # запуск процессов
        for i in range(num_processes):
            start_row = i * rows_per_process
            end_row = start_row + rows_per_process
            if i == num_processes - 1:
                end_row += extra_rows
            
            p = multiprocessing.Process(
                target=multiply_partial,
                args=(matrix_a, matrix_b, start_row, end_row, i, log_queue, result_queue)
            )
            processes.append(p)
            p.start()
        
        # сбор результатов
        results = []
        for _ in range(num_processes):
            results.append(result_queue.get())
        
        # Ожидание зав
        for p in processes:
            p.join()
        
        # Объединение результатов
        result_matrix = combine_results(results, a_rows, b_cols)
        
        end_time = time.time()
        
        # вывод рез
        log_message(f"Result matrix ({a_rows}x{b_cols}):\n{result_matrix}", log_queue)
        log_message(f"Multiplication completed in {end_time - start_time:.4f} seconds", log_queue)
        
        # сохранение итогового результата
        with open("final_result.txt", 'w') as f:
            for row in result_matrix:
                f.write(' '.join(map(str, row)) + '\n')
        log_message("Final result saved to final_result.txt", log_queue)
        
    except Exception as e:
        log_message(f"Error: {str(e)}", log_queue)
    finally:
        # заверш процес лог
        stop_logging_event.set()
        logger.join()
        log_queue.close()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()