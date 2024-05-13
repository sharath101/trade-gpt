import { createChart } from 'lightweight-charts';
import { useEffect, useState, useRef } from 'react';
import { io } from 'socket.io-client';

const URL = 'http://localhost:5000';
export const socket = io(URL);

function timeout(delay) {
    return new Promise(res => setTimeout(res, delay));
}

export const ChartComponent = () => {
    const [isConnected, setIsConnected] = useState(socket.connected);
    const [candleData, setCandleData] = useState([]);

    const chartContainerRef = useRef();
    const chartRef = useRef(null); // Ref to store the chart instance
    if (isConnected) {}
    
    useEffect(() => {
        

        function onConnect() {
            setIsConnected(true);
            socket.emit("backtest_all", { "time": 0 });
        }

        function onDisconnect() {
            setIsConnected(false);
        }

        async function onBacktestEvent(value) {
            if (value) {
                setCandleData(previous => [...previous, ...value]);
                let lastTimestamp = value[value.length - 1]["time"];
                socket.emit("backtest_next", { "time": lastTimestamp });
            } else {
                await timeout(0.1);
                let lastTimestamp = candleData[candleData.length - 1]["time"];
                socket.emit("backtest_next", { "time": lastTimestamp });
            }
        }

        function onBacktestAll(value) {
            setCandleData(previous => [...previous, ...value.all]);
            let lastTimestamp = value.all[value.all.length - 1]["time"];
            socket.emit("backtest_next", { "time": lastTimestamp });
        }

        socket.on('connect', onConnect);
        socket.on('disconnect', onDisconnect);
        socket.on('backtest_next', onBacktestEvent);
        socket.on('backtest_all', onBacktestAll);

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

        return () => {
            window.removeEventListener('resize', handleResize);
            // Don't remove the chart instance here
            socket.off('connect', onConnect);
            socket.off('disconnect', onDisconnect);
            socket.off('backtest_next', onBacktestEvent);
            socket.off('backtest_all', onBacktestAll);
        };
    }, [candleData]);

    return <div ref={chartContainerRef} />;
};
