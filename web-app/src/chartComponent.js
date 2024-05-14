import { createChart } from 'lightweight-charts';
import { useEffect, useState, useRef } from 'react';
import { io } from 'socket.io-client';

const URL = 'http://localhost:5000';
export const socket = io(URL);

function timeout(delay) {
    return new Promise(res => setTimeout(res, delay));
}

function useChartData() {
    const [isConnected, setIsConnected] = useState(socket.connected);
    const [candleData, setCandleData] = useState([]);

    useEffect(() => {
        if (isConnected) {}
        function onConnect() {
            setIsConnected(true);
            socket.emit("backtest", { "start": 0, })
        }

        function onDisconnect() {
            setIsConnected(false);
        }

        function onBacktest(value) {
            setCandleData(previous => [...value.all]);
            let last_timestamp = value.all[value.all.length - 1]["time"];
            socket.emit("backtest", { "start": last_timestamp, "stop": 0 })
        }

        socket.on('connect', onConnect);
        socket.on('disconnect', onDisconnect);
        socket.on('backtest', onBacktest);

        return () => {
            socket.off('connect', onConnect);
            socket.off('disconnect', onDisconnect);
            socket.off('backtest', onBacktest);
        };
    }, [candleData, isConnected]);

    return { candleData };
}

export const ChartComponent = () => {
    const { candleData } = useChartData();
    const chartContainerRef = useRef(null);
    const chartRef = useRef(null);
    
    useEffect(() => {
        const handleResize = () => {
            if (chartRef.current) {
                const chartOptions = {
                    layout: { textColor: 'black', background: { type: 'solid', color: 'white' } },
                    width: chartContainerRef.current.clientWidth,
                    height: window.innerHeight, // Adjust chart height to window height
                };
                chartRef.current.chart.applyOptions(chartOptions);
            }
        };

        if (!chartRef.current) {
            // Create the chart instance if it doesn't exist     
            const chartOptions = {
                layout: { textColor: 'black', background: { type: 'solid', color: 'white' } },
                width: chartContainerRef.current.clientWidth,
                height: window.innerHeight, // Adjust chart height to window height
            };      
            const chart = createChart(chartContainerRef.current, chartOptions);
            const candleSeries = chart.addCandlestickSeries({
                lineColor: '#2962FF',
                topColor: '#2962FF',
                bottomColor: 'rgba(41, 98, 255, 0.28)',
            });
            chartRef.current = { chart, candleSeries }; // Save chart instance to the ref
        }

        // Update chart data whenever candleData changes
        chartRef.current.candleSeries.setData(candleData);
        window.addEventListener('resize', handleResize);

        function myVisibleTimeRangeChangeHandler(newVisibleTimeRange) {
            if (newVisibleTimeRange === null) {
                // handle null
            }
        //     console.log("-------------------")
        //     console.log(newVisibleTimeRange.from);
        //     console.log(newVisibleTimeRange.to);
        }
        
        chartRef.current.chart.timeScale().subscribeVisibleTimeRangeChange(myVisibleTimeRangeChangeHandler);

        return () => {
            window.removeEventListener('resize', handleResize);
        };
    }, [candleData]);

    return <div ref={chartContainerRef} />;
};
