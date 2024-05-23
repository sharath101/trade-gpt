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

export function useWebsocket() {
    const [largerCandleData, setLargerCandleData] = useState(() => {
        return [];
    });
    const [retryData, setRetryData] = useState({});
    const [gotData, setGotData] = useState({});

    useEffect(() => {
        function onConnect() {
            socket.emit('backtest', { start: 0, end: 0});
        }

        function onBacktest(value) {
            console.log(value);
            if (value && value.data && value.data.length) {
                const newarr = mergeAndSortArrays(largerCandleData, value.data);
                setLargerCandleData(newarr);
                timeout(100).then(() => {
                    setRetryData((previous) => ({retry: !previous.retry}));
                    setGotData((previous) => ({retry: !previous.retry}));
                });
            }
            else {
                timeout(100).then(() => {
                    setRetryData((previous) => ({retry: !previous.retry}));
                });
            }
        }
        socket.on('connect', onConnect);
        socket.on('backtest', onBacktest);

        return () => {
            socket.off('connect', onConnect);
            socket.off('backtest', onBacktest);
        };


    }, [largerCandleData]);

    return { largerCandleData, retryData,  gotData}

}

export function useChartData() {
    const [candleData, setCandleData] = useState(() => {
        return [];
    });
    const [newRequest, setNewRequest] = useState(() => {
        return {start: 0, end: 0};
    });
    const [winPosition, setWinPosition] = useState(() => {
        return {start: 0, end: 0};
    });
    const {largerCandleData, retryData, gotData} = useWebsocket();

    useEffect(() => {
        // Check largerCandleData if required data is available
        // Set candleData to required window (with some buffer)
        // winPosition is the position in window user currently looking at
        let [from] = largerCandleData.filter((val) => {
            return val.time === winPosition.start
        });
        let [to]= largerCandleData.filter((val) => {
            return val.time === winPosition.end
        });
        
        if (largerCandleData.length) {
            // Get the 100 candles on the left if buffer is smaller than 100 candles
            if (from && from.index - largerCandleData[0].index <= 300 && largerCandleData[0].index) {
                setNewRequest((previous) => ({
                    start: largerCandleData[0].index - 300 <= 0 ? 0 : largerCandleData[0].index - 300, 
                    end: largerCandleData[0].index
                }));
            }

            // Get the  candles on the right if buffer is smaller than 100 candles
            if (to && largerCandleData[largerCandleData.length-1].index - to.index <= 100) {
                setNewRequest((previous) => ({
                    start: largerCandleData[largerCandleData.length-1].index + 1, 
                    end: largerCandleData[largerCandleData.length-1].index + 101
                }));
            }
            setCandleData((previous) => (largerCandleData));
        }
        else {
            setNewRequest((previous) => ({
                start: null, 
                end: null
            }));

        }
        return () => {

        };
    }, [ largerCandleData, winPosition, gotData]);

    useEffect(() => {
        // Fetch reqeust new data from server
        console.log("spamming");
        socket.emit("backtest", {"start": newRequest.start, "end": newRequest.end})
    }, [newRequest])

    return { candleData, setWinPosition};
}