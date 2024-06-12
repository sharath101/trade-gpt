import { useState, useEffect } from 'react';
import { userService } from '../axiosConfig';

export function LandingPage({ setPage }) {
    const [check, setCheck] = useState();

    useEffect(() => {
        const checkLogin = async (event) => {
            const response = await userService.get('/check_login');
            if (response.data['status'] === 'success') {
                localStorage.setItem(
                    'auth',
                    response.headers.get('Authorization')
                );
                setPage('dashboard');
            } else {
                setPage('signin');
            }
        };

        checkLogin();
    }, [check, setCheck, setPage]);

    return <div></div>;
}
