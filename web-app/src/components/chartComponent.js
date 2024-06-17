import { createChart } from 'lightweight-charts';
import { useEffect, useRef } from 'react';
import { useChartData } from '../hooks/useChartData';

export const ChartComponent = ({ setPage }) => {
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
                    crosshair: 0,
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
            const areaSeries = chart.addAreaSeries({
                lastValueVisible: false,
                //crosshairMarkerVisible: false,
                lineColor: 'transparent',
                topColor: 'rgba(56, 33, 110,0.6)',
                bottomColor: 'rgba(56, 33, 110, 0.1)',
            });

            chartRef.current = { chart, candleSeries, areaSeries };
        }

        if (candleData && candleData.length) {
            const lineData = candleData.map((datapoint) => ({
                time: datapoint.time,
                value: (datapoint.close + datapoint.open) / 2,
            }));

            chartRef.current.candleSeries.setData(candleData);
            chartRef.current.areaSeries.setData(lineData);
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
                .unsubscribeVisibleTimeRangeChange(
                    handleVisibleTimeRangeChange
                );
            window.removeEventListener('resize', handleResize);
        };
    }, [candleData, setWinPosition]);

    return <div ref={chartContainerRef} />;
};
