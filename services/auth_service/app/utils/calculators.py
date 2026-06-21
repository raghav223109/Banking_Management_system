def calculate_emi(principal: float, annual_interest_rate: float, months: int) -> float:
    """
    EMI = [P x R x (1+R)^N]/[(1+R)^N-1]
    P = Principal, R = Monthly Interest, N = Months
    """
    if annual_interest_rate == 0:
        return principal / months
        
    monthly_rate = annual_interest_rate / (12 * 100)
    emi = (principal * monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
    return round(emi, 2)
