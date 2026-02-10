import { useEffect, useState } from 'react';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export function useTeams() {
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchTeams();
  }, []);

  const fetchTeams = async () => {
    try {
      const response = await axios.get(`${API_BASE}/teams`);
      setTeams(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch teams');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return { teams, loading, error };
}

export function useMatches(type: 'upcoming' | 'recent' = 'upcoming') {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchMatches();
  }, [type]);

  const fetchMatches = async () => {
    try {
      const endpoint = type === 'upcoming' ? 'matches/upcoming' : 'matches/recent';
      const response = await axios.get(`${API_BASE}/${endpoint}?limit=20`);
      setMatches(response.data);
      setError(null);
    } catch (err) {
      setError(`Failed to fetch ${type} matches`);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return { matches, loading, error, refetch: fetchMatches };
}

export function usePrediction(matchId: number) {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (matchId) {
      fetchPrediction();
    }
  }, [matchId]);

  const fetchPrediction = async () => {
    try {
      const response = await axios.get(`${API_BASE}/predict/match/${matchId}/detailed`);
      setPrediction(response.data.prediction);
      setError(null);
    } catch (err) {
      setError('Failed to fetch prediction');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return { prediction, loading, error };
}

export function useTeamForm(teamId: number, matches: number = 5) {
  const [form, setForm] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (teamId) {
      fetchForm();
    }
  }, [teamId, matches]);

  const fetchForm = async () => {
    try {
      const response = await axios.get(
        `${API_BASE}/teams/${teamId}/form?matches=${matches}`
      );
      setForm(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch team form');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return { form, loading, error };
}
