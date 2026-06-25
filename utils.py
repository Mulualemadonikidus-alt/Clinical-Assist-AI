def calculate_dosage(drug, weight):
    """
    Returns (display_dose, is_alert)
    """
    if drug['type'] == 'weight_based':
        dose = round(drug['factor'] * weight, 2)
        is_alert = dose > drug['max_dose']
        return f"{dose} {drug['unit']}", is_alert
    
    elif drug['type'] == 'infusion':
        # Returns the range provided in JSON
        return f"{drug['range']} {drug['unit']}", False
        
    else: # static
        return f"{drug['dose']} {drug['unit']}", False