import { createChart, ColorType } from 'lightweight-charts';
import React, { useEffect, useState, useRef } from 'react';
import data from './constants.js';
import { io } from 'socket.io-client';

const URL = 'http://localhost:5000';

export const socket = io(URL);

const cData = data.initialData;
const realTimeData = data.realtimeUpdates;

export const ChartComponent = (props) => {
    // const [candleData, setCandleData] = useState([]);
    // setCandleData(cData);
    const [isConnected, setIsConnected] = useState(socket.connected);
    const [candleData, setcandleData] = useState([]);

    const {
        // candleData,
        // data,
        colors: {
            backgroundColor = 'dark',
            lineColor = '#2962FF',
            textColor = 'white',
            areaTopColor = '#2962FF',
            areaBottomColor = 'rgba(41, 98, 255, 0.28)',
        } = {},
    } = props;

    const chartContainerRef = useRef();

    useEffect(() => {
        function onConnect() {
            console.log('connected');
            setIsConnected(true);
        }

        function onDisconnect() {
            console.log('disconnected');
            setIsConnected(false);
        }

        function onBacktestEvent(value) {
            setcandleData((previous) => [...previous, value]);
        }

        socket.on('connect', onConnect);
        socket.on('disconnect', onDisconnect);
        socket.on('backtest', onBacktestEvent);

        if (candleData.length == 1000) {
            setcandleData();
        }

        const handleResize = () => {
            chart.applyOptions({
                width: chartContainerRef.current.clientWidth,
            });
        };

        const chart = createChart(chartContainerRef.current, {
            layout: {
                background: { color: '#222' },
                textColor: '#DDD',
            },
            grid: {
                vertLines: { color: '#444' },
                horzLines: { color: '#444' },
            },
            width: chartContainerRef.current.clientWidth,
            height: 500,
        });
        chart.timeScale().fitContent();

        // const newSeries = chart.addAreaSeries({
        //     lineColor,
        //     topColor: areaTopColor,
        //     bottomColor: areaBottomColor,
        // });
        // newSeries.setData(data);

        const candleSeries = chart.addCandlestickSeries({
            lineColor,
            topColor: areaTopColor,
            bottomColor: areaBottomColor,
        });
        candleSeries.setData(candleData);

        // simulate real-time data
        // function* getNextRealtimeUpdate(realtimeData) {
        //     for (const dataPoint of realtimeData) {
        //         yield dataPoint;
        //     }
        //     return null;
        // }
        // const streamingDataProvider = getNextRealtimeUpdate(realTimeData);

        // const intervalID = setInterval(() => {
        //     const update = streamingDataProvider.next();
        //     if (update.done) {
        //         clearInterval(intervalID);
        //         return;
        //     }
        //     candleSeries.update(update.value);
        // }, 100);

        // window.addEventListener('resize', handleResize);

        // const datesForMarkers = [
        //     candleData[candleData.length - 39],
        //     candleData[candleData.length - 19],
        // ];
        // let indexOfMinPrice = 0;
        // for (let i = 1; i < datesForMarkers.length; i++) {
        //     if (
        //         datesForMarkers[i].high < datesForMarkers[indexOfMinPrice].high
        //     ) {
        //         indexOfMinPrice = i;
        //     }
        // }

        // const markers = [
        //     {
        //         time: candleData[candleData.length - 48].time,
        //         position: 'aboveBar',
        //         color: '#f68410',
        //         shape: 'circle',
        //         text: 'D',
        //     },
        // ];
        // for (let i = 0; i < datesForMarkers.length; i++) {
        //     if (i !== indexOfMinPrice) {
        //         markers.push({
        //             time: datesForMarkers[i].time,
        //             position: 'aboveBar',
        //             color: '#e91e63',
        //             shape: 'arrowDown',
        //             text: 'Sell @ ' + Math.floor(datesForMarkers[i].high + 2),
        //         });
        //     } else {
        //         markers.push({
        //             time: datesForMarkers[i].time,
        //             position: 'belowBar',
        //             color: '#2196F3',
        //             shape: 'arrowUp',
        //             text: 'Buy @ ' + Math.floor(datesForMarkers[i].low - 2),
        //         });
        //     }
        // }
        // candleSeries.setMarkers(markers);

        chart.timeScale().fitContent();

        return () => {
            window.removeEventListener('resize', handleResize);

            chart.remove();
            socket.off('connect', onConnect);
            socket.off('disconnect', onDisconnect);
            socket.off('backtest', onBacktestEvent);
        };
    }, [
        candleData,
        backgroundColor,
        lineColor,
        textColor,
        areaTopColor,
        areaBottomColor,
    ]);

    return <div ref={chartContainerRef} />;
};

const initialData = [
    { time: '2018-12-22', value: 32.51 },
    { time: '2018-12-23', value: 31.11 },
    { time: '2018-12-24', value: 27.02 },
    { time: '2018-12-25', value: 27.32 },
    { time: '2018-12-26', value: 25.17 },
    { time: '2018-12-27', value: 28.89 },
    { time: '2018-12-28', value: 25.46 },
    { time: '2018-12-29', value: 23.92 },
    { time: '2018-12-30', value: 22.68 },
    { time: '2018-12-31', value: 22.67 },
];

function App(props) {
    return (
        <ChartComponent
            {...props}
            // data={initialData}
            // candleData={cna}
        ></ChartComponent>
    );
}

export default App;
