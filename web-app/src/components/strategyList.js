import React, { useEffect, useState } from 'react';
import { strategyService } from '../axiosConfig';
import {
    Container,
    Typography,
    List,
    ListItem,
    ListItemText,
    CircularProgress,
    Button,
    Box,
    Checkbox,
    ListItemSecondaryAction,
    IconButton,
} from '@mui/material';
import { Delete } from '@mui/icons-material';

export const StrategyListPage = ({ setPage, setStrategy }) => {
    const [strategies, setStrategies] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedStrategies, setSelectedStrategies] = useState([]);

    useEffect(() => {
        strategyService
            .get('/strategy')
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

    const handleAddStrategy = () => {
        setStrategy(null);
        setPage('strategyEditor');
    };

    const handleSelectStrategy = (strategyId) => {
        setSelectedStrategies((prevSelected) =>
            prevSelected.includes(strategyId)
                ? prevSelected.filter((id) => id !== strategyId)
                : [...prevSelected, strategyId]
        );
    };

    const handleDeleteStrategies = async () => {
        try {
            await Promise.all(
                selectedStrategies.map((strategyId) =>
                    strategyService.delete(`/strategy/${strategyId}`)
                )
            );
            setStrategies((prevStrategies) =>
                prevStrategies.filter(
                    (strategy) => !selectedStrategies.includes(strategy.id)
                )
            );
            setSelectedStrategies([]);
        } catch (error) {
            console.error('Error deleting strategies:', error);
        }
    };

    if (loading) {
        return <CircularProgress />;
    }

    return (
        <Container>
            <Box
                display='flex'
                justifyContent='space-between'
                alignItems='center'
                mb={2}
            >
                <Typography variant='h4'>Strategies</Typography>
                <Box>
                    <Button
                        variant='contained'
                        color='primary'
                        onClick={handleAddStrategy}
                    >
                        Add Strategy
                    </Button>
                    <Button
                        variant='contained'
                        color='secondary'
                        onClick={handleDeleteStrategies}
                        disabled={selectedStrategies.length === 0}
                        style={{ marginLeft: '10px' }}
                    >
                        Delete Selected
                    </Button>
                </Box>
            </Box>
            <List>
                {strategies.map((strategy) => (
                    <ListItem
                        key={strategy.id}
                        button
                        onClick={() => handleStrategyClick(strategy.id)}
                    >
                        <Checkbox
                            edge='start'
                            checked={selectedStrategies.includes(strategy.id)}
                            tabIndex={-1}
                            disableRipple
                            onChange={() => handleSelectStrategy(strategy.id)}
                        />
                        <ListItemText
                            primary={strategy.strategy_name}
                            secondary={strategy.description}
                        />
                        <ListItemSecondaryAction>
                            <IconButton
                                edge='end'
                                onClick={() =>
                                    handleSelectStrategy(strategy.id)
                                }
                            >
                                <Delete />
                            </IconButton>
                        </ListItemSecondaryAction>
                    </ListItem>
                ))}
            </List>
        </Container>
    );
};
