import { useEffect, useState } from 'react';
import { io } from 'socket.io-client';

const URL = 'http://localhost:5000';
export const socket = io(URL);

function timeout(delay) {
    return new Promise((res) => setTimeout(res, delay));
}

function mergeAndSortArrays(arr1, arr2) {
    const combinedArray = [...arr1, ...arr2];
    combinedArray.sort((a, b) => a.time - b.time);
    const uniqueTimestamps = new Set();
    const uniqueArray = [];
    for (const item of combinedArray) {
        if (!uniqueTimestamps.has(item.time)) {
            uniqueArray.push(item);
            uniqueTimestamps.add(item.time);
        }
    }
    return uniqueArray;
}

export function useChartData() {
    const [isConnected, setIsConnected] = useState(socket.connected);
    const [allCandleData, setAllCandleData] = useState([]);
    const [timeWindow, setTimeWindow] = useState({ start: 0, end: 0 });
    let next_data = {};

    useEffect(() => {
        function onConnect() {
            setIsConnected(true);
            socket.emit('backtest', { start: 0, end: 0});
        }

        function onDisconnect() {
            setIsConnected(false);
        }

        function onBacktest(value) {
            if (value && value.data && value.data.length) {
                const newarr = mergeAndSortArrays(allCandleData, value.data);
                setAllCandleData(newarr);
                socket.emit('backtest_next', { last: newarr[newarr.length-1].time, num: 10 });
                timeout(50);
                next_data = { last: newarr[newarr.length-1].time, num: 10 };
            }
            else {
                timeout(50);
                next_data = { last: allCandleData[allCandleData.length-1].time, num: 10 };
                socket.emit('backtest_next', next_data);
            }
            
        }

        socket.on('connect', onConnect);
        socket.on('disconnect', onDisconnect);
        socket.on('backtest', onBacktest);

        return () => {
            socket.off('connect', onConnect);
            socket.off('disconnect', onDisconnect);
            socket.off('backtest', onBacktest);
        };
    }, [allCandleData, isConnected, timeWindow]);

    // Emit the timeWindow whenever it changes
    useEffect(() => {
        socket.emit('backtest', { start: timeWindow.start, end: timeWindow.end });
    }, [timeWindow]);

    return { candleData: allCandleData, setTimeWindow };
}

