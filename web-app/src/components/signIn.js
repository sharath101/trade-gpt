import { useState } from 'react';
import Avatar from '@mui/material/Avatar';
import Button from '@mui/material/Button';
import Alert from '@mui/material/Alert';
import TextField from '@mui/material/TextField';
import Link from '@mui/material/Link';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import Typography from '@mui/material/Typography';
import Card from '@mui/material/Card';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { GoogleOAuthProvider } from '@react-oauth/google';
import { GoogleLogin } from '@react-oauth/google';
import { userService } from '../axiosConfig';

function Copyright(props) {
    return (
        <Typography
            variant='body2'
            color='text.secondary'
            align='center'
            {...props}
        >
            {'Copyright © '}
            <Link color='inherit'>Trade GPT</Link> {new Date().getFullYear()}
            {'.'}
        </Typography>
    );
}

// TODO remove, this demo shouldn't need to reset the theme.

const defaultTheme = createTheme();

export function SignInSide({ setPage }) {
    const [message, setMessage] = useState();
    <GoogleLogin
        onSuccess={(credentialResponse) => {
            console.log(credentialResponse);
        }}
        onError={() => {
            console.log('Login Failed');
        }}
    />;

    const handleGoogleLoginSuccess = async (response) => {
        // Handle successful Google login
        console.log(response);
        const tokenId = response.credential;
        // Send tokenId to your backend for verification and authentication
        // You can use axios to make a POST request to your backend
        try {
            const res = await userService.get(
                '/login/callback'.concat('?code=', tokenId)
            );
            // Handle successful backend authentication
            if (res.data['status'] === 'success') {
                localStorage.setItem(
                    'auth',
                    response.headers.get('Authorization')
                );
                setPage('dashboard');
            } else {
                setMessage(response.data['message']);
            }
            setPage('dashboard');
        } catch (error) {
            setMessage('Failed to authenticate with Google');
        }
    };

    const handleGoogleLoginFailure = (error) => {
        console.log(error);
        // Handle Google login failure
        // setMessage(error);
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        const data = new FormData(event.currentTarget);

        let loginData = {
            email: data.get('email'),
            password: data.get('password'),
        };

        const response = await userService.post('/login', loginData, {
            headers: {
                'Content-Type': 'application/json',
            },
        });
        if (response.data['status'] === 'success') {
            localStorage.setItem('auth', response.headers.get('Authorization'));
            setPage('dashboard');
        } else {
            setMessage(response.data['message']);
        }
    };

    return (
        <GoogleOAuthProvider clientId='90994580365-acodsgurvahlumvdec4piddbmq6ubsrp.apps.googleusercontent.com'>
            <ThemeProvider theme={defaultTheme}>
                <Card
                    sx={{
                        maxWidth: 'sm',
                        my: 8,
                        mx: 4,
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                    }}
                >
                    <Grid item xs={12} sm={8} md={5} elevation={6}>
                        <Box
                            sx={{
                                my: 8,
                                mx: 4,
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'center',
                            }}
                        >
                            <Avatar sx={{ m: 1, bgcolor: 'secondary.main' }}>
                                <LockOutlinedIcon />
                            </Avatar>
                            <Typography component='h1' variant='h5'>
                                Sign in
                            </Typography>
                            <Box
                                component='form'
                                noValidate
                                onSubmit={handleSubmit}
                                sx={{ mt: 1 }}
                            >
                                <TextField
                                    margin='normal'
                                    required
                                    fullWidth
                                    id='email'
                                    label='Email Address'
                                    name='email'
                                    autoComplete='email'
                                    autoFocus
                                    onChange={() => setMessage('')}
                                />
                                <TextField
                                    margin='normal'
                                    required
                                    fullWidth
                                    name='password'
                                    label='Password'
                                    type='password'
                                    id='password'
                                    autoComplete='current-password'
                                    onChange={() => setMessage('')}
                                />
                                {message && (
                                    <Alert severity='error'>{message}</Alert>
                                )}
                                <Button
                                    type='submit'
                                    fullWidth
                                    variant='contained'
                                    sx={{ mt: 3, mb: 2 }}
                                >
                                    Sign In
                                </Button>
                                <Grid container>
                                    <Grid item xs>
                                        <GoogleLogin
                                            onSuccess={handleGoogleLoginSuccess}
                                            onError={handleGoogleLoginFailure}
                                        />
                                    </Grid>

                                    <Grid item>
                                        <Button
                                            variant='outlined'
                                            color='secondary'
                                            onClick={() => {
                                                setPage('register');
                                            }}
                                        >
                                            Sign Up
                                        </Button>
                                    </Grid>
                                </Grid>
                                <Copyright sx={{ mt: 5 }} />
                            </Box>
                        </Box>
                    </Grid>
                </Card>
            </ThemeProvider>
        </GoogleOAuthProvider>
    );
}
