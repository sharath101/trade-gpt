import { createChart } from 'lightweight-charts';
import { useEffect, useRef } from 'react';
import { useChartData } from '../hooks/useChartData';


export const ChartComponent = () => {
    const { candleData, setWinPosition } = useChartData();
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
                    height: window.innerHeight,
                };
                chartRef.current.chart.applyOptions(chartOptions);
            }
        };

        if (!chartRef.current) {
            const chartOptions = {
                layout: {
                    textColor: 'black',
                    background: { type: 'solid', color: 'white' },
                },
                width: chartContainerRef.current.clientWidth,
                height: window.innerHeight,
            };
            const chart = createChart(chartContainerRef.current, chartOptions);
            const candleSeries = chart.addCandlestickSeries({
                lineColor: '#2962FF',
                topColor: '#2962FF',
                bottomColor: 'rgba(41, 98, 255, 0.28)',
            });
            chartRef.current = { chart, candleSeries };
        }

        if (candleData && candleData.length) {
            chartRef.current.candleSeries.setData(candleData);
        }
        window.addEventListener('resize', handleResize);

        const handleVisibleTimeRangeChange = (newVisibleTimeRange) => {
            if (newVisibleTimeRange === null) {
                console.error('VisibleTimeRange is null');
                return;
            }
            const adjustedTimeWindow = {
                start: newVisibleTimeRange.from,
                end: newVisibleTimeRange.to,
            };

            setWinPosition(adjustedTimeWindow);
        };
        
        chartRef.current.chart
            .timeScale()
            .subscribeVisibleTimeRangeChange(handleVisibleTimeRangeChange);

        return () => {
            chartRef.current.chart
            .timeScale()
            .unsubscribeVisibleTimeRangeChange(handleVisibleTimeRangeChange);
            window.removeEventListener('resize', handleResize);
        };
    }, [candleData, setWinPosition]);

    return <div ref={chartContainerRef} />;
};
