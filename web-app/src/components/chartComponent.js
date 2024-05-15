import { createChart } from 'lightweight-charts';
import { useEffect, useState, useRef } from 'react';
import { useChartData } from '../hooks/useChartData';


export const ChartComponent = () => {
    const { candleData, setTimeWindow } = useChartData();
    const chartContainerRef = useRef(null);
    const chartRef = useRef(null);

    useEffect(() => {
        const handleResize = () => {
            if (chartRef.current) {
                const chartOptions = {
                    layout: {
                        textColor: 'black',
                        background: { type: 'solid', color: 'white' },
                    },
                    width: chartContainerRef.current.clientWidth,
                    height: window.innerHeight, // Adjust chart height to window height
                };
                chartRef.current.chart.applyOptions(chartOptions);
            }
        };

        if (!chartRef.current) {
            // Create the chart instance if it doesn't exist
            const chartOptions = {
                layout: {
                    textColor: 'black',
                    background: { type: 'solid', color: 'white' },
                },
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
        if (candleData && candleData.length) {
            chartRef.current.candleSeries.setData(candleData);
        }
        window.addEventListener('resize', handleResize);

        const handleVisibleTimeRangeChange = (newVisibleTimeRange) => {
            if (newVisibleTimeRange === null) {
                console.error('VisibleTimeRange is null');
                return;
            }
            console.log(newVisibleTimeRange.from);
            const adjustedTimeWindow = {
                start: (newVisibleTimeRange.from - 432000),
                end: (newVisibleTimeRange.to + 5000),
            };
    
            // Update state with the adjusted time window
            setTimeWindow(adjustedTimeWindow);
    
            // Fetch new data based on adjustedTimeWindow and update candleData
        };
        
        chartRef.current.chart
            .timeScale()
            .subscribeVisibleTimeRangeChange(handleVisibleTimeRangeChange);

        return () => {
            window.removeEventListener('resize', handleResize);
        };
    }, [candleData]);

    return <div ref={chartContainerRef} />;
};
