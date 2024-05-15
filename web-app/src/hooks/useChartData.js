import { useEffect, useState } from 'react';
import { io } from 'socket.io-client';

const URL = 'http://localhost:5000';
export const socket = io(URL);

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

export function useChartData(timeWindow) {
    const [isConnected, setIsConnected] = useState(socket.connected);
    const [allCandleData, setAllCandleData] = useState([]);
    // const [candleData, setCandleData] = useState([]);

    useEffect(() => {
        if (isConnected) {
        }
        function onConnect() {
            setIsConnected(true);
            console.log('connected');
            socket.emit('backtest', { start: -1 });
        }

        function onDisconnect() {
            setIsConnected(false);
        }

        function onBacktest(value) {
            if (value && value.data && value.data.length) {
                // const newarr = mergeAndSortArrays(allCandleData, value.data);
                setAllCandleData((previousData) => value.data);
                console.log(`after merge: ${allCandleData.length}`);
            }
            let last_timestamp = -1;
            if (allCandleData.length) {
                last_timestamp =
                    allCandleData[allCandleData.length - 1]['time'];
            }
            socket.emit('backtest', {
                start: timeWindow.start - 1000,
                end: timeWindow.end + 1000,
            });
        }

        socket.on('connect', onConnect);
        socket.on('disconnect', onDisconnect);
        socket.on('backtest', onBacktest);

        return () => {
            socket.off('connect', onConnect);
            socket.off('disconnect', onDisconnect);
            socket.off('backtest', onBacktest);
        };
    }, [allCandleData, isConnected]);

    return { candleData: allCandleData };
}
