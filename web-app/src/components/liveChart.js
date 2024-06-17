import React, { useEffect, useRef } from 'react';
import { createChart } from 'lightweight-charts';
import axios from 'axios';
import io from 'socket.io-client';

const URL = 'http://localhost:5003';
export const socket = io(URL);

function onConnect() {
    console.log('Connected to LiveLink');
}

socket.on('connect', onConnect);

export const LiveChart = ({ setPage }) => {
    const chartContainerRef = useRef(null);
    const chartRef = useRef(null);
    const candleSeriesRef = useRef(null);

    // Initialize the chart once when the component mounts
    useEffect(() => {
        chartRef.current = createChart(chartContainerRef.current, {
            width: chartContainerRef.current.clientWidth,
            height: 400,
            layout: {
                backgroundColor: '#ffffff',
                textColor: '#000000',
            },
            grid: {
                vertLines: {
                    color: '#eeeeee',
                },
                horzLines: {
                    color: '#eeeeee',
                },
            },
            priceScale: {
                borderColor: '#cccccc',
            },
            timeScale: {
                borderColor: '#cccccc',
            },
        });

        // Create a candlestick series
        candleSeriesRef.current = chartRef.current.addCandlestickSeries();

        // Clean up on unmount
        return () => {
            if (chartRef.current) {
                chartRef.current.remove();
            }
        };
    }, []); // Empty dependency array ensures this runs once on mount

    // Set up the API call and socket connection once when the component mounts
    useEffect(() => {
        const startLiveData = async () => {
            try {
                // Call the API to start the live data
                // await axios.get('http://your-backend-url/live/start/BTCUSDT');

                // Connect to the socket server
                const socket = io('http://127.0.0.1:5003');

                // socket.on('connect', onConnect);

                // Listen for candle data and update the chart
                socket.on('candle_data', (candle) => {
                    console.log(candle);
                    candleSeriesRef.current.update(candle);
                });

                // Clean up on unmount
                return () => {
                    socket.disconnect();
                };
            } catch (error) {
                console.error('Error starting live data:', error);
            }
        };

        startLiveData();
    }, []); // Empty dependency array ensures this runs once on mount

    return (
        <div
            ref={chartContainerRef}
            style={{ position: 'relative', width: '100%', height: '400px' }}
        />
    );
};
