import React, { useEffect, useState } from 'react';
import axios from '../axiosConfig';
import {
    Container,
    Typography,
    List,
    ListItem,
    ListItemText,
    CircularProgress,
} from '@mui/material';

export const StrategyListPage = ({ setPage, setStrategy }) => {
    const [strategies, setStrategies] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        axios
            .get('/get_strategies')
            .then((response) => {
                setStrategies(response.data['data']);
                setLoading(false);
            })
            .catch((error) => {
                console.error(
                    'There was an error fetching the strategies!',
                    error
                );
                setLoading(false);
            });
    }, []);

    const handleStrategyClick = (strategyId) => {
        setStrategy(strategyId);
        setPage('strategyEditor');
    };

    if (loading) {
        return <CircularProgress />;
    }

    return (
        <Container>
            <Typography variant='h4'>Strategies</Typography>
            <List>
                {strategies.map((strategy) => (
                    <ListItem
                        button
                        key={strategy.id}
                        onClick={() => handleStrategyClick(strategy.id)}
                    >
                        <ListItemText
                            primary={strategy.strategy_name}
                            secondary={strategy.description}
                        />
                    </ListItem>
                ))}
            </List>
        </Container>
    );
};
