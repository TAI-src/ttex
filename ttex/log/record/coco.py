from ttex.log.record import Record, Header

class COCORecord(Record):
    template = "{f_evals} {g_evals} {best_dist_opt:+.9e} {mf:+.9e} {best_mf:+.9e} {x_str}"
    def __init__(self, f_evals: int, g_evals: int, best_dist_opt: float, mf: float, best_mf: float, x: list):
        """
        Initialize a COCO step with the given parameters.

        Args:
            f_evals (int): Number of function evaluations.
            g_evals (int): Number of gradient evaluations.
            best_dist_opt(float): Best noise-free fitness minus the optimal function value + sum g_i+
            mf (float): Measured fitness.
            best_mf (float): Best measured fitness or single-digit g-values.
            x (list): List containing the x values.
        """
        self.f_evals = f_evals
        self.g_evals = g_evals
        self.best_dist_opt = best_dist_opt 
        self.mf = mf
        self.best_mf = best_mf
        self.x = x

    def __str__(self):
        """
        Format the COCO step as a string.
        Returns:
            str: Formatted COCO step string.
        """
        x_str = " ".join(f"{val:+.4e}" for val in self.x)
        return COCORecord.template.format(
            f_evals=self.f_evals,
            g_evals=self.g_evals,
            best_dist_opt=self.best_dist_opt,
            mf=self.mf,
            best_mf=self.best_mf,
            x_str=x_str
        )

class COCOHeader(Header):
    template = "% f evaluations | g evaluations | best noise-free fitness - Fopt ({fopt:.12e}) + sum g_i+ | measured fitness | best measured fitness or single-digit g-values | x1 | x2..."
    def __init__(self, fopt: float):
        """
        Initialize a COCO header with the optimal function value.

        Args:
            fopt (float): Optimal function value.
        """
        self.fopt = fopt


    def __str__(self):
        """
        Format the COCO header with the optimal function value.

        Returns:
            str: Formatted header string.
        """
        return COCOHeader.template.format(fopt=self.fopt)

    
