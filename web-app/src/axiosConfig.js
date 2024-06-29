import axios from 'axios';

const setupInterceptors = (instance) => {
    instance.interceptors.request.use(
        (config) => {
            const token = localStorage.getItem('auth');
            if (token) {
                config.headers['Authorization'] = `Bearer ${token}`;
            }
            return config;
        },
        (error) => {
            return Promise.reject(error);
        }
    );
};

export const createAxiosInstance = (baseURL) => {
    const instance = axios.create({
        baseURL: baseURL,
    });
    setupInterceptors(instance);
    return instance;
};

export const userService = createAxiosInstance('http://127.0.0.1:5000');
export const strategyService = createAxiosInstance('http://127.0.0.1:5002');
export const backtestService = createAxiosInstance('http://127.0.0.1:5001');
export const liveService = createAxiosInstance('http://127.0.0.1:5003');
