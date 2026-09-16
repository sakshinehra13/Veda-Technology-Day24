import time
import asyncio
import threading
import multiprocessing
import streamlit as st
import matplotlib.pyplot as plt

# --- Workload Definitions ---
def cpu_bound_task(n):
    return sum(i * i for i in range(n))

def run_multiprocessing_benchmark(n, num_processes):
    start = time.time()
    # Use multiprocessing Pool
    with multiprocessing.Pool(processes=num_processes) as pool:
        pool.map(cpu_bound_task, [n] * num_processes)
    return time.time() - start

def io_bound_task_sync(delay):
    time.sleep(delay)

def run_threading_benchmark(delay, num_threads):
    start = time.time()
    threads = [threading.Thread(target=io_bound_task_sync, args=(delay,)) for _ in range(num_threads)]
    for t in threads: t.start()
    for t in threads: t.join()
    return time.time() - start

async def io_bound_task_async(delay):
    await asyncio.sleep(delay)

async def main_async(delay, num_tasks):
    await asyncio.gather(*(io_bound_task_async(delay) for _ in range(num_tasks)))

def run_asyncio_benchmark(delay, num_tasks):
    start = time.time()
    asyncio.run(main_async(delay, num_tasks))
    return time.time() - start


# --- Streamlit Application Layout ---
st.set_page_config(page_title="Python Concurrency Benchmarker", layout="wide")

st.title("⚡ Python Concurrency: Threading, Multiprocessing, and AsyncIO")
st.markdown("Compare performance characteristics, understand execution time differences, and study use cases interactively.")

# Sidebar Controls for Customization
st.sidebar.header("🛠️ Benchmark Configuration")
cpu_n = st.sidebar.slider("CPU-Bound Workload Size (Iterations)", 1_000_000, 10_000_000, 5_000_000, 1_000_000)
cpu_processes = st.sidebar.slider("Number of Processes / Workers", 1, 8, 4)

io_delay = st.sidebar.slider("I/O-Bound Simulated Delay (seconds)", 0.1, 2.0, 1.0, 0.1)
io_tasks = st.sidebar.slider("Number of I/O Tasks / Threads", 1, 20, 5)

tab1, tab2, tab3 = st.tabs(["🚀 Live Benchmark & Visualizer", "📖 Detailed Explanations", "❓ Interview Q&A"])

with tab1:
    st.subheader("Live Performance Execution")
    st.markdown("Run benchmarks live based on your custom configuration panel parameters on the left.")

    if st.button("Run All Benchmarks", type="primary"):
        with st.spinner("Running Multiprocessing (CPU-bound)..."):
            mp_time = run_multiprocessing_benchmark(cpu_n, cpu_processes)
        
        with st.spinner("Running Threading (I/O-bound)..."):
            th_time = run_threading_benchmark(io_delay, io_tasks)
            
        with st.spinner("Running AsyncIO (I/O-bound)..."):
            async_time = run_asyncio_benchmark(io_delay, io_tasks)

        st.success("Benchmarks completed successfully!")

        # Display Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Multiprocessing Time", f"{mp_time:.4f}s")
        col2.metric("Threading Time", f"{th_time:.4f}s")
        col3.metric("AsyncIO Time", f"{async_time:.4f}s")

        # Plotting results
        st.markdown("### 📊 Performance Comparison Chart")
        fig, ax = plt.subplots(figsize=(8, 4))
        approaches = ['Multiprocessing\n(CPU-bound)', 'Threading\n(I/O-bound)', 'AsyncIO\n(I/O-bound)']
        times = [mp_time, th_time, async_time]
        colors = ['#ff9999','#66b3ff','#99ff99']
        
        ax.bar(approaches, times, color=colors)
        ax.set_ylabel('Execution Time (Seconds)')
        ax.set_title('Concurrency Model Speed Comparison')
        
        for i, v in enumerate(times):
            ax.text(i, v + 0.05, f"{v:.4f}s", ha='center', fontweight='bold')

        st.pyplot(fig)

with tab2:
    st.subheader("📖 When to use which concurrency model?")
    
    st.markdown("""
    ### 1. Multiprocessing
    * **What it does:** Spawns separate, independent instances of Python interpreters, each running in its own memory space.
    * **Why use it:** Bypasses the **Global Interpreter Lock (GIL)** entirely by utilizing multiple CPU cores.
    * **Ideal Use Cases:** Heavy mathematical computing, image processing, machine learning data pre-processing, video encoding.

    ### 2. Threading
    * **What it does:** Uses operating system-level threads within the same memory space.
    * **Why use it:** Great for traditional blocking operations where threads wait on external systems. 
    * **Ideal Use Cases:** Multi-file disk I/O, reading/writing database legacy streams, standard blocking network calls.

    ### 3. AsyncIO
    * **What it does:** Cooperative, single-threaded concurrency governed by an event loop (`async`/`await`).
    * **Why use it:** Extremely lightweight; handles thousands of simultaneous connections without context-switching costs of OS threads.
    * **Ideal Use Cases:** Web scraping, building asynchronous web APIs (FastAPI/Aiohttp), real-time chat servers.
    """)

with tab3:
    st.subheader("❓ Core Interview Questions & Answers")
    
    with st.expander("1. What is the Python GIL (Global Interpreter Lock)?"):
        st.write("The GIL is a mutex (or a lock) used by CPython to protect access to Python objects, preventing multiple native threads from executing Python bytecodes at once. This simplifies CPython memory management, but limits performance on multi-core processors for multithreaded CPU-bound programs.")

    with st.expander("2. When should multiprocessing be used over threading?"):
        st.write("Multiprocessing should be used when your task is **CPU-bound** (computation heavy). Because threads share the same memory space and are throttled by the GIL, adding threads to a CPU-bound task will not utilize multiple cores. Multiprocessing avoids this by running separate processes on distinct CPU cores.")

    with st.expander("3. When is AsyncIO most useful?"):
        st.write("AsyncIO is most useful for **I/O-bound** applications with high concurrency needs (like handling 10,000 simultaneous web socket connections). Because it doesn't spin up full OS threads, overhead is minimal and context switching is explicitly managed via event loops.")

    with st.expander("4. Why doesn't adding threads always improve performance?"):
        st.write("Adding threads introduces context-switching overhead. Furthermore, due to the GIL, threads contending for CPU execution time can actually slow down performance rather than speed it up. Threads only improve performance when tasks spend most of their time waiting (I/O-bound).")